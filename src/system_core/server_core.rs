//! This handles communication between clients and the server

use crate::system_core::message::{MessageToClient, MessageToServer};
use crate::system_core::objects::UserObject;
use lazy_static::lazy_static;
use std::net::SocketAddr;
use std::time::Duration;
use tokio::sync::mpsc::{unbounded_channel, UnboundedReceiver, UnboundedSender};
use tokio::sync::RwLock;
use tokio::time::sleep;
use crate::system_core::commands::run_command;

pub async fn get_users_len() -> usize {
    CLIENTS.read().await.iter().filter(|c| c.is_auth()).count()
}

pub async fn register_connection(
    peer: SocketAddr,
) -> (
    UnboundedSender<MessageToServer>,
    UnboundedReceiver<MessageToClient>,
) {
    let (tc_tx, tc_rx) = unbounded_channel::<MessageToClient>();
    let (ts_tx, ts_rx) = unbounded_channel::<MessageToServer>();
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
        user: UserObject,
    },
    UserMessage {
        author: UserObject,
        content: String,
    },
    Remove,
    RunCommand {
        name: String,
        args: Vec<String>,
    },
    ClientShutdownR {
        reason: String,
    }
}

async fn get_events() -> Vec<(Event, usize)> {
    let mut events = vec![];
    CLIENTS.write().await.iter_mut().enumerate().for_each(|(i, conn)| {
        if let Some(event) = match conn.rx.try_recv() {
            Ok(MessageToServer::Authorize { user }) => {
                Some(Event::Authorize { user })
            }
            Ok(MessageToServer::Message { content }) => {
                conn.get_user().map(|author| Event::UserMessage { author, content })
            }
            Ok(MessageToServer::RemoveMe) => {
                Some(Event::Remove)
            }
            Ok(MessageToServer::RunCommand { name, args }) => {
                Some(Event::RunCommand { name, args })
            },
            Ok(MessageToServer::ClientDisconnect { reason }) => {
                Some(Event::ClientShutdownR { reason })
            },
            _ => None
        } {
            events.push((event, i));
        }
    });
    events
}

async fn send_to_all(what: MessageToClient, authed_only: bool) {
    CLIENTS.write().await.iter_mut().filter(|conn| !authed_only || conn.is_auth()).for_each(|conn| {
        conn.tx.send(what.clone()).unwrap();
    });
}

pub async fn core_thread() {
    loop {
        let events = get_events().await;
        for (event, i) in events {
            match event {
                Event::Authorize { user} => {
                    CLIENTS.write().await.get_mut(i).unwrap().auth(&user);
                },
                Event::UserMessage { author, content } => {
                    send_to_all(MessageToClient::UserMessage { author, content }, true).await;
                }
                Event::Remove => {
                    CLIENTS.write().await.get_mut(i).unwrap().disconnect();

                },
                Event::RunCommand { name, args } => {
                    run_command(name, args, CLIENTS.write().await.get_mut(i).unwrap()).await;
                },
                Event::ClientShutdownR { reason } => {
                    CLIENTS.write().await.get_mut(i).unwrap().tx.send(MessageToClient::SystemMessage {
                        content: reason
                    }).unwrap();

                    CLIENTS.write().await.get_mut(i).unwrap().disconnect();
                }
            }
        }
        sleep(Duration::from_millis(50)).await;
    }
}

pub struct Connection {
    pub state: State,
    pub tx: UnboundedSender<MessageToClient>,
    pub rx: UnboundedReceiver<MessageToServer>,
    pub peer_addr: SocketAddr,
}

impl Connection {
    pub fn auth(&mut self, user: &UserObject) {
        self.state = State::Authorized(user.clone());
    }

    pub fn is_auth(&self) -> bool {
        matches!(self.state, State::Authorized(_))
    }

    pub fn get_user(&self) -> Option<UserObject> {
        match &self.state {
            State::Authorized(user) => Some(user.clone()),
            _ => None,
        }
    }

    pub fn disconnect(&mut self) {
        self.tx.send(MessageToClient::Shutdown).unwrap();
        self.state = State::Disconnected;
    }
}

pub enum State {
    Unauthorized,
    Authorized(UserObject),
    Disconnected,
}

lazy_static! {
    pub static ref CLIENTS: RwLock<Vec<Connection>> = RwLock::new(Vec::new());
}
