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

    pub const fn is_auth(&self) -> bool {
        matches!(self.state, ConnectionState::Authenticated(_))
    }

    pub fn auth(&mut self, user: User) {
        self.state = ConnectionState::Authenticated(user);
    }

    pub fn get_user(&self) -> Option<User> {
        match self.state.clone() {
            ConnectionState::Unauthenticated => None,
            ConnectionState::Authenticated(u) => Some(u),
        }
    }
}

pub struct Connection {
    pub to_client: UnboundedSender<MessageToClient>,
    pub from_client: UnboundedReceiver<MessageFromClient>,
    pub addr: SocketAddr,
    pub state: ConnectionState,
}

#[derive(Clone)]
pub enum ConnectionState {
    Unauthenticated,
    Authenticated(User),
}
