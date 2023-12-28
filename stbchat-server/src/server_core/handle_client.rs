use std::io;
use std::io::ErrorKind;

use log::{error, info};
use tokio::net::TcpStream;
use tokio::sync::mpsc::{UnboundedReceiver, UnboundedSender};

use stbchat::packet::ServerboundPacket;
use stbchat::read_write::read_packet;

use crate::message::{MessageFromClient, MessageToClient};

pub async fn handle_client(
    mut stream: TcpStream,
    rx: UnboundedReceiver<MessageToClient>,
    tx: UnboundedSender<MessageFromClient>,
) {
    let peer_addr = stream.peer_addr().unwrap();
    loop {
        let packet: ServerboundPacket = match read_packet(&mut stream).await {
            Ok(p) => p,
            Err(e) => {
                if matches!(
                    e.downcast_ref::<io::Error>().map(io::Error::kind),
                    Some(ErrorKind::ConnectionReset | ErrorKind::UnexpectedEof)
                ) {
                    info!("{peer_addr} closed connection");
                    return;
                }
                dbg!(&e);
                error!("Could not read packet from {peer_addr}: {e}");
                continue;
            }
        };
        match packet {
            ServerboundPacket::Authenticate { user, password } => {
                info!("{peer_addr} attempted to log in as {user}")
            }
            ServerboundPacket::Register { .. } => {}
            ServerboundPacket::MessageSend { .. } => {}
            ServerboundPacket::CommandRun { .. } => {}
        }
    }
}
