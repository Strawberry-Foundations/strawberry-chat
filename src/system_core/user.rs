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

impl ClientSender {
    pub fn new(client: TcpStream) -> Self {
        let addr = &client.peer_addr().unwrap().ip().clone();

        Self {
            socket: client,
            address: *addr
        }
    }

    pub async fn send(&mut self, message: impl ToString) {
        self.socket.write_all(
            message.to_string().as_bytes()).await.unwrap_or_else(
            |_| LOGGER.error(
                log_parser(COMMUNICATION_ERROR, &[&self.address, &"placeholder"]
                )
            )
        );
    }
}