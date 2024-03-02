use std::net::IpAddr;

use tokio::io::{AsyncWriteExt, ReadHalf, WriteHalf};
use tokio::net::TcpStream;
use tokio::sync::mpsc::{Receiver, Sender};

use owo_colors::OwoColorize;
use stblib::colors::{BOLD, C_RESET, GRAY, YELLOW};

use stblib::stbm::stbchat::net::{IncomingPacketStream, OutgoingPacketStream};
use stblib::stbm::stbchat::object::User;
use stblib::stbm::stbchat::packet::{ClientPacket, ServerPacket};

use crate::constants::log_messages::{CLIENT_KICKED, USER_LEFT};
use crate::global::{LOGGER, MESSAGE_VERIFICATOR};
use crate::security::verification::MessageAction;
use crate::system_core::log::log_parser;
use crate::system_core::message::{MessageToClient, MessageToServer};
use crate::system_core::string::StbString;

pub async fn client_incoming(
    tx: Sender<MessageToServer>,
    mut r_stream: IncomingPacketStream<ReadHalf<TcpStream>>,
    peer_addr: IpAddr,
    user: User,
) {
    loop {
        // TODO: Replace unwraps with logger errors + RemoveMe
        let msg = match r_stream.read::<ServerPacket>().await {
            Ok(ServerPacket::Message { message }) => message,
            Err(e) => {
                LOGGER.warning(format!("Failed to read packet, received from {peer_addr}: {e}"));
                break;
            }
            _ => continue,
        };

        let content = strip_ansi_escapes::strip_str(msg);

        if content.starts_with('/') && content.len() > 1 {
            let parts: Vec<String> = content[1..]
                .split_ascii_whitespace()
                .map(String::from)
                .collect();

            if &parts[0] == "exit" {
                tx.send(MessageToServer::Broadcast {
                    content: format!("{GRAY}{BOLD}-->{C_RESET} {}{}{YELLOW}{BOLD} left the chat room!{C_RESET}", user.role_color, user.username)
                }).await.unwrap();

                tx.send(MessageToServer::RemoveMe).await.unwrap();
                LOGGER.info(log_parser(USER_LEFT, &[&user.username, &peer_addr]));
                return;
            }

            tx.send(MessageToServer::RunCommand {
                name: parts[0].to_string(),
                args: parts[1..].to_vec(),
            })
                .await
                .unwrap();
            continue;
        }

        let action = MESSAGE_VERIFICATOR.check(&content.to_lowercase());

        match action {
            MessageAction::Kick => {
                tx.send(MessageToServer::Broadcast {
                    content: format!("{GRAY}{BOLD}-->{C_RESET} {}{}{YELLOW}{BOLD} left the chat room!{C_RESET}", user.role_color, user.username)
                }).await.unwrap();

                tx.send(MessageToServer::ClientDisconnect {
                    reason: "Please be friendlier in the chat. Rejoin when you feel ready!"
                        .yellow()
                        .bold()
                        .to_string(),
                })
                    .await
                    .unwrap();

                LOGGER.info(log_parser(
                    CLIENT_KICKED,
                    &[&peer_addr, &"Used blacklisted word"],
                ));
            }
            MessageAction::Hide => {}
            MessageAction::Allow => tx.send(MessageToServer::Message { content }).await.unwrap(),
        }
    }
}

pub async fn client_outgoing(
    mut rx: Receiver<MessageToClient>,
    mut w_stream: OutgoingPacketStream<WriteHalf<TcpStream>>,
    peer_addr: IpAddr,
) {
    loop {
        let Some(msg) = rx.recv().await else {
            return;
        };

        match msg {
            MessageToClient::UserMessage { author, content } => {
                let content = StbString::from_str(content)
                    .apply_htpf()
                    .check_for_mention()
                    .await;

                if let Err(e) = w_stream.write(ClientPacket::UserMessage {
                    author,
                    message: content.string,
                }).await {
                    LOGGER.error(format!("[S -> {peer_addr}] Failed to send a packet: {e}"));
                    return;
                }
            }
            MessageToClient::SystemMessage { content } => {
                if let Err(e) = w_stream
                    .write(ClientPacket::SystemMessage {
                        message: content,
                    })
                    .await
                {
                    LOGGER.error(format!("[S -> {peer_addr}] Failed to send a packet: {e}"));
                    return;
                }
            }
            MessageToClient::Shutdown => {
                let _ = w_stream.unwrap().shutdown().await;
                return;
            }
        }
    }
}