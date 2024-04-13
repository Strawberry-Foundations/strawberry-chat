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
use crate::constants::log_messages::SEND_INTERNAL_MESSAGE_FAIL;
use crate::global::{CORE_VERSION, LOGGER};

const CHANNEL_BUFFER: usize = 10;

pub struct Core {
    pub online_users: u16
}

impl Core {
    pub fn new() -> Self {
        Self {
            online_users: 0
        }
    }

    pub fn add_connection(&mut self) {
        self.online_users += 1;
    }
}

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
enum Event {
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
    Remove,
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
        if let Some(event) = match conn.rx.try_recv() {
            Ok(MessageToServer::Authorize { user }) => {
                Some(Event::Authorize { user })
            },
            Ok(MessageToServer::Message { content }) => {
                conn.get_user().map(|author| Event::UserMessage { author, content })
            },
            Ok(MessageToServer::Broadcast { content }) => {
                conn.get_user().map(|_| Event::SystemMessage { content })
            },
            Ok(MessageToServer::RemoveMe) => {
                Some(Event::Remove)
            },
            Ok(MessageToServer::RunCommand { name, args }) => {
                Some(Event::RunCommand { name, args })
            },
            Ok(MessageToServer::ClientDisconnect { reason }) => {
                Some(Event::ClientShutdownR { reason })
            },
            Ok(MessageToServer::ClientNotification { content, bell, sent_by}) => {
                Some(Event::ClientNotification { content, bell, sent_by })
            },
            Ok(MessageToServer::SystemMessage { content}) => {
                Some(Event::SystemMessageToUser { content })
            }
            _ => None
        } {
            events.push((event, i));
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
    LOGGER.info(format!("Starting core thread ({})", CORE_VERSION.clone()));

    loop {
        let _ = watchdog_tx.try_send(());
        let events = get_events().await;
        
        for (event, i) in events {
            match event {
                Event::Authorize { user} => {
                    CLIENTS.write().await.get_mut(i).unwrap().auth(&user);
                },
                Event::UserMessage { author, content } => {
                    send_to_all(MessageToClient::UserMessage { author, content }, true).await;
                },
                Event::Remove => {
                    CLIENTS.write().await.get_mut(i).unwrap().disconnect().await;
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
                    CLIENTS.write()
                        .await.get_mut(i).unwrap()
                        .tx.send(MessageToClient::SystemMessage { content }).await.unwrap();
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

lazy_static! {
    pub static ref CLIENTS: RwLock<Vec<Connection>> = RwLock::new(Vec::new());
}