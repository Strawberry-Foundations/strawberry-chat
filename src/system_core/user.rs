use std::net::IpAddr;

use tokio::io::AsyncWriteExt;
use tokio::net::TcpStream;

use crate::constants::log_messages::COMMUNICATION_ERROR;
use crate::global::LOGGER;
use crate::system_core::log::log_parser;

pub struct ClientSender {
    pub socket: TcpStream,
    pub address: IpAddr
}

pub struct UserObject {
    pub username: String,
    pub nickname: String,
    pub badge: char,
    pub role_color: String,
    pub avatar_url: String,
}

impl ClientSender {
    pub fn new(client: TcpStream) -> Self {
        let addr = &client.peer_addr().unwrap().ip().clone();

        Self {
            socket: client,
            address: *addr
        }
    }

    pub async fn send<M: ToString + Send>(&mut self, message: M) {
        self.socket.write_all(
            message.to_string().as_bytes()).await.unwrap_or_else(
            |_| LOGGER.error(
                log_parser(COMMUNICATION_ERROR, &[&self.address, &"placeholder"]
                )
            )
        );
    }
}