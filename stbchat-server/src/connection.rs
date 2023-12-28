use std::net::SocketAddr;

use tokio::net::TcpStream;
use tokio::sync::mpsc::{UnboundedReceiver, UnboundedSender};

use stbchat::user::User;

use crate::message::{MessageFromClient, MessageToClient};

impl Connection {
    pub fn new(
        stream: &TcpStream,
        rx: UnboundedReceiver<MessageFromClient>,
        tx: UnboundedSender<MessageToClient>,
    ) -> Self {
        Self {
            to_client: tx,
            from_client: rx,
            addr: stream.peer_addr().unwrap(),
            state: ConnectionState::Unauthenticated,
        }
    }
}

pub struct Connection {
    to_client: UnboundedSender<MessageToClient>,
    from_client: UnboundedReceiver<MessageFromClient>,
    addr: SocketAddr,
    state: ConnectionState,
}

pub enum ConnectionState {
    Unauthenticated,
    Authenticated(User),
}
