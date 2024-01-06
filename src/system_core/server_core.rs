//! This handles communication between clients and the server

use crate::system_core::message::{MessageToClient, MessageToServer};
use crate::system_core::user::UserObject;
use lazy_static::lazy_static;
use std::net::SocketAddr;
use tokio::sync::mpsc::{unbounded_channel, UnboundedReceiver, UnboundedSender};
use tokio::sync::RwLock;

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

struct Connection {
    state: State,
    tx: UnboundedSender<MessageToClient>,
    rx: UnboundedReceiver<MessageToServer>,
    peer_addr: SocketAddr,
}

enum State {
    Unauthorized,
    Authorized(UserObject),
}

lazy_static! {
    static ref CLIENTS: RwLock<Vec<Connection>> = RwLock::new(Vec::new());
}
