use std::io;
use std::io::ErrorKind;
use std::net::SocketAddr;

use log::{error, info};
use tokio::io::{split, ReadHalf, WriteHalf};
use tokio::net::TcpStream;
use tokio::sync::mpsc::{UnboundedReceiver, UnboundedSender};
use tokio::{select, spawn};

use stbchat::packet::{ClientboundPacket, ServerboundPacket};
use stbchat::read_write::{read_packet, write_packet};
use stbchat::user::User;

use crate::message::{MessageFromClient, MessageToClient};

async fn handle_stream_c2s(
    mut client_r: ReadHalf<TcpStream>,
    peer_addr: SocketAddr,
    tx: UnboundedSender<MessageFromClient>,
) {
    loop {
        let packet: ServerboundPacket = match read_packet(&mut client_r).await {
            Ok(p) => p,
            Err(e) => {
                if matches!(
                    e.downcast_ref::<io::Error>().map(io::Error::kind),
                    Some(ErrorKind::ConnectionReset | ErrorKind::UnexpectedEof)
                ) {
                    info!("{peer_addr} closed connection");
                    tx.send(MessageFromClient::RemoveMe)
                        .expect("Failed to sent event through channel");
                    return;
                }
                error!("Could not read packet from {peer_addr}: {e}");
                continue;
            }
        };
        match packet {
            ServerboundPacket::Authenticate { user, password } => {
                info!("{peer_addr} attempted to log in as '{user}'");
                tx.send(MessageFromClient::Authenticated {
                    user: User {
                        name: user.clone(),
                        nick: user,
                        member_since: 0,
                    },
                })
                .expect("Failed to sent event through channel");
            }
            ServerboundPacket::Register { .. } => {
                todo!()
            }
            ServerboundPacket::MessageSend { content } => {
                tx.send(MessageFromClient::SentMessage { content })
                    .expect("Failed to send event through channel");
            }
            ServerboundPacket::CommandRun { .. } => {
                todo!()
            }
        }
    }
}

async fn handle_stream_s2c(
    mut client_w: WriteHalf<TcpStream>,
    peer_addr: SocketAddr,
    mut rx: UnboundedReceiver<MessageToClient>,
) {
    loop {
        let Some(msg) = rx.recv().await else { return };
        match msg {
            MessageToClient::ReceiveUserMessage { user, content } => {
                let packet = ClientboundPacket::UserMessageReceive {
                    author: user,
                    content,
                };
                write_packet(&packet, &mut client_w).await.unwrap();
            }
            MessageToClient::ReceiveSystemMessage { content } => {
                let packet = ClientboundPacket::SystemMessageReceive { raw: content };
                write_packet(&packet, &mut client_w)
                    .await
                    .expect("Failed to write packet");
            }
            MessageToClient::Disconnect { reason } => {
                let packet = ClientboundPacket::Disconnect { reason };
                write_packet(&packet, &mut client_w)
                    .await
                    .expect("Failed to write packet");
                panic!("Client was disconnected by server")
            }
        }
    }
}

pub async fn handle_client(
    stream: TcpStream,
    rx: UnboundedReceiver<MessageToClient>,
    tx: UnboundedSender<MessageFromClient>,
) {
    let peer_addr = stream.peer_addr().unwrap();
    let (client_r, client_w) = split(stream);
    let c2s = spawn(handle_stream_c2s(client_r, peer_addr, tx));
    let s2c = spawn(handle_stream_s2c(client_w, peer_addr, rx));
    select! {
        _ = c2s => info!("C->S for {peer_addr} closed"),
        _ = s2c => info!("S->C for {peer_addr} closed"),
    }
}
