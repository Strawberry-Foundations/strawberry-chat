use std::net::IpAddr;
use tokio::net::TcpStream;

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
}