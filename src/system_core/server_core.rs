//! This handles communication between clients and the server

use std::net::SocketAddr;
use std::time::Duration;

use tokio::sync::mpsc::{channel, Receiver, Sender};
use tokio::sync::RwLock;
use tokio::time::sleep;

use stblib::stbchat::object::User;
use stblib::utilities::escape_ansi;
use lazy_static::lazy_static;

use crate::system_core::commands::run_command;
use crate::system_core::internals::{MessageToClient, MessageToServer};
use crate::system_core::string::StbString;
use crate::system_core::status::{Status, UserStatus};
use crate::constants::log_messages::SEND_INTERNAL_MESSAGE_FAIL;
use crate::global::{CORE_VERSION, LOGGER, RUNTIME_LOGGER};

const CHANNEL_BUFFER: usize = 10;

pub async fn get_users_len() -> usize {
    CLIENTS.read().await.iter().filter(|c| c.is_auth()).count()
}

pub async fn get_online_usernames() -> Vec<String> {
    CLIENTS.read().await.iter().filter_map(|c| c.get_user().map(|u| u.username)).collect()
}

pub async fn get_online_users() -> Vec<User> {
    CLIENTS.read().await.iter().filter_map(Connection::get_user).collect()
}

pub async fn get_senders_by_username(username: &str) -> Vec<Sender<MessageToClient>> {
    CLIENTS.read().await
        .iter()
        .filter(|c| c.get_user().map(|u| u.username) == Some(username.to_string()))
        .map(|c| c.tx.clone())
        .collect()
}

pub async fn get_senders_by_username_ignore_case(username: &str) -> Vec<Sender<MessageToClient>> {
    CLIENTS.read().await
        .iter()
        .filter(|c| c.get_user().is_some_and(|u| u.username.eq_ignore_ascii_case(username)))
        .map(|c| c.tx.clone())
        .collect()
}

pub async fn register_connection(peer: SocketAddr) -> (Sender<MessageToServer>, Receiver<MessageToClient>, ) {
    let (tc_tx, tc_rx) = channel::<MessageToClient>(CHANNEL_BUFFER);
    let (ts_tx, ts_rx) = channel::<MessageToServer>(CHANNEL_BUFFER);

    CLIENTS.write().await.push(
        Connection {
            state: State::Unauthorized,
            tx: tc_tx,
            rx: ts_rx,
            peer_addr: peer
        }
    );

    (ts_tx, tc_rx)
}

#[derive(Debug)]
pub enum Event {
    Authorize {
        user: User,
    },
    UserMessage {
        author: User,
        content: String,
    },
    SystemMessage {
        content: String,
    },
    SystemMessageToUser {
        content: String,
    },
    Remove {
        username: Option<String>
    },
    RunCommand {
        name: String,
        args: Vec<String>,
    },
    ClientShutdownR {
        reason: String,
    },
    ClientNotification {
        content: StbString,
        bell: bool,
        sent_by: User
    },
}

async fn get_events() -> Vec<(Event, usize)> {
    let mut events = vec![];

    CLIENTS.write().await.iter_mut().enumerate().for_each(|(i, conn)| {
        if let Some(message) = match conn.rx.try_recv().ok() {
            Some(MessageToServer::Authorize { user }) => {
                Some(Event::Authorize { user })
            },
            Some(MessageToServer::Message { content }) => {
                conn.get_user().map(|author| Event::UserMessage { author, content })
            },
            Some(MessageToServer::Broadcast { content }) => {
                conn.get_user().map(|_| Event::SystemMessage { content })
            },
            Some(MessageToServer::RemoveMe { username}) => {
                Some(Event::Remove { username })
            },
            Some(MessageToServer::RunCommand { name, args }) => {
                Some(Event::RunCommand { name, args })
            },
            Some(MessageToServer::ClientDisconnect { reason }) => {
                Some(Event::ClientShutdownR { reason })
            },
            Some(MessageToServer::ClientNotification { content, bell, sent_by}) => {
                Some(Event::ClientNotification { content, bell, sent_by })
            },
            Some(MessageToServer::SystemMessage { content}) => {
                Some(Event::SystemMessageToUser { content })
            }
            _ => None
        } {
            events.push((message, i));
        }
    });
    events
}

#[allow(clippy::significant_drop_in_scrutinee)]
pub async fn send_to_all(what: MessageToClient, authed_only: bool) {
    for conn in CLIENTS.read().await.iter().filter(|conn| !authed_only || conn.is_auth()) {
        let _ = conn.tx.send(what.clone()).await;
    }
}

pub async fn core_thread(watchdog_tx: Sender<()>) {
    RUNTIME_LOGGER.info(format!("Starting core thread ({})", CORE_VERSION.clone()));

    loop {
        let _ = watchdog_tx.try_send(());
        let events = get_events().await;
        
        for (event, i) in events {
            if CLIENTS.read().await[i].get_user().is_some_and(has_hook_sync) {
                let conn = &mut CLIENTS.write().await[i];
                send_to_hook_sync(conn.get_user().unwrap(), event);
                continue
            }

            match event {
                Event::Authorize { user} => {
                    CLIENTS.write().await.get_mut(i).unwrap().auth(&user);
                    STATUS.write().await.append(user.username.as_str(), Status::Online);
                },
                Event::UserMessage { author, content } => {
                    send_to_all(MessageToClient::UserMessage { author, content }, true).await;
                },
                Event::Remove { username }=> {
                    CLIENTS.write().await.get_mut(i).unwrap().disconnect().await;

                    if let Some(username) = username {
                        STATUS.write().await.remove(username.as_str());
                    }
                },
                Event::RunCommand { name, args } => {
                    run_command(name, args, CLIENTS.read().await.get(i).unwrap()).await;
                },
                Event::ClientShutdownR { reason } => {
                    CLIENTS.write().await.get_mut(i).unwrap().tx.send(MessageToClient::SystemMessage {
                        content: reason
                    }).await.unwrap();
                    CLIENTS.write().await.get_mut(i).unwrap().disconnect().await;
                },
                Event::SystemMessage { content } => {
                    send_to_all(MessageToClient::SystemMessage { content }, true).await;
                },
                Event::SystemMessageToUser { content } => {
                    CLIENTS.write().await.get_mut(i).unwrap().tx.send(MessageToClient::SystemMessage { content }).await.unwrap();
                },
                Event::ClientNotification { content, bell, sent_by} => {
                    let conn = get_senders_by_username(content.mentioned_user.as_str()).await;

                    for tx in conn {
                        let username = if sent_by.username == sent_by.nickname {
                            sent_by.username.to_string()
                        }
                        else {
                            format!("{} (@{})", sent_by.nickname, sent_by.username)
                        };

                        tx.send(MessageToClient::Notification {
                            title: String::from("Strawberry Chat"),
                            username,
                            avatar_url: sent_by.avatar_url.clone(),
                            content: escape_ansi(content.string.as_str()),
                            bell,
                        }).await.unwrap_or_else(|e| {
                            LOGGER.error(format!("Failed to send internal packet: {e}"));
                        });
                    }
                }
            }
        }
        CLIENTS.write().await.retain(|c| c.state != State::Disconnected);
        sleep(Duration::from_millis(60)).await;
    }
}

pub struct Connection {
    pub state: State,
    pub tx: Sender<MessageToClient>,
    pub rx: Receiver<MessageToServer>,
    pub peer_addr: SocketAddr,
}

impl Connection {
    pub fn auth(&mut self, user: &User) {
        self.state = State::Authorized(user.clone());
    }

    pub fn is_auth(&self) -> bool {
        matches!(self.state, State::Authorized(_))
    }

    pub fn get_user(&self) -> Option<User> {
        match &self.state {
            State::Authorized(user) => Some(user.clone()),
            _ => None,
        }
    }

    pub async fn disconnect(&mut self) {
        self.tx.send(MessageToClient::Shutdown).await.unwrap_or_else(|_| LOGGER.warning(SEND_INTERNAL_MESSAGE_FAIL));
        self.state = State::Disconnected;
    }
}

#[derive(PartialEq, Eq)]
pub enum State {
    Unauthorized,
    Authorized(User),
    Disconnected,
}

struct EventHook {
    pub(crate) from_user: User,
    detour: Sender<Event>,
    amount_uses: usize,
}

pub async fn register_hook(detour: Sender<Event>, from_user: User, amount_uses: usize) -> bool {
    if has_hook(from_user.clone()).await {
        return false;
    }
    EVENT_HOOKS.write().await.push(EventHook { from_user, detour, amount_uses });
    true
}

fn has_hook_sync(who: User) -> bool {
    futures::executor::block_on(has_hook(who))
}

async fn has_hook(who: User) -> bool {
    EVENT_HOOKS.read().await.iter().any(|h| h.from_user == who)
}

pub async fn remove_hooks_by_user(user: User) {
    EVENT_HOOKS.write().await.retain(|h| h.from_user != user);
}

#[allow(clippy::needless_pass_by_value)]
fn send_to_hook_sync(who: User, what: Event) -> bool {
    futures::executor::block_on(async {
        let mut w_guard = EVENT_HOOKS.write().await;
        let maybe_detour = w_guard
            .iter_mut()
            .find(|h| h.from_user == who);

        if let Some(hook) = maybe_detour {
            if hook.detour.send(what).await.is_err() {
                return false;
            };
        } else {
            return false;
        }

        w_guard.retain_mut(|h| {
            if h.from_user == who {
                h.amount_uses -= 1;
                if h.amount_uses == 0 {
                    return false;
                }
            }
            
            true
        });
        true
    })
}

lazy_static! {
    pub static ref CLIENTS: RwLock<Vec<Connection>> = RwLock::new(Vec::new());
    static ref EVENT_HOOKS: RwLock<Vec<EventHook>> = RwLock::new(Vec::new());
    pub static ref STATUS: RwLock<UserStatus> = RwLock::new(UserStatus::new());
}