//! This handles communication between clients and the server

use crate::system_core::message::{MessageToClient, MessageToServer};
use crate::system_core::user::UserObject;
use lazy_static::lazy_static;
use std::net::SocketAddr;
use tokio::sync::mpsc::{unbounded_channel, UnboundedReceiver, UnboundedSender};
use tokio::sync::RwLock;

pub async fn get_users_len() -> usize {
    CLIENTS.read().await.len()
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

enum Event {
    Authorize {
        idx: usize,
        user: UserObject
    },
    UserMessage {
        author: UserObject,
        content: String
    },
    Remove {
        idx: usize
    },
}

async fn get_events() -> Vec<Event> {
    let mut events = vec![];
    for (i, connection) in CLIENTS.write().await.iter_mut().enumerate() {
        match connection.rx.try_recv() {
            Ok(MessageToServer::Authorize { user }) => {
                events.push(Event::Authorize { idx: i, user });
            }
            Ok(MessageToServer::Message { content }) => {
                if let Some(author) = connection.get_user() {
                    events.push(Event::UserMessage { author: author.clone(), content });
                }
            }
            Ok(MessageToServer::RemoveMe) => {
                events.push(Event::Remove { idx: i });
            }
            _ => {}
        }
    };
    events
}

async fn send_to_all(what: MessageToClient, authed_only: bool) {
    for conn in CLIENTS.write().await.iter_mut() {
        if authed_only && !conn.is_auth() {
            continue;
        }
        conn.tx.send(what.clone()).unwrap();
    }
}

pub async fn core_thread() {
    loop {
        let events = get_events().await;
        for event in events {
            match event {
                Event::Authorize { idx, user} => {
                    CLIENTS.write().await.get_mut(idx).unwrap().auth(&user);
                },
                Event::UserMessage { author, content } => {
                    send_to_all(MessageToClient::UserMessage {author, content}, true).await;
                }
                Event::Remove { idx } => {
                    CLIENTS.write().await.remove(idx);
                }
            }
        }
    }
}

struct Connection {
    state: State,
    tx: UnboundedSender<MessageToClient>,
    rx: UnboundedReceiver<MessageToServer>,
    peer_addr: SocketAddr,
}

impl Connection {
    fn auth(&mut self, user: &UserObject) {
        self.state = State::Authorized(user.clone());
    }

    fn is_auth(&self) -> bool {
        matches!(self.state, State::Authorized(_))
    }

    fn get_user(&self) -> Option<&UserObject> {
        match &self.state {
            State::Authorized(user) => Some(user),
            State::Unauthorized => None,
        }
    }
}

enum State {
    Unauthorized,
    Authorized(UserObject),
}

lazy_static! {
    static ref CLIENTS: RwLock<Vec<Connection>> = RwLock::new(Vec::new());
}
