use std::io::ErrorKind;
use std::net::IpAddr;

use tokio::io::{AsyncWriteExt, ReadHalf, WriteHalf};
use tokio::net::TcpStream;
use tokio::sync::mpsc::{Receiver, Sender};

use owo_colors::OwoColorize;

use stblib::stbchat::net::{IncomingPacketStream, OutgoingPacketStream};
use stblib::stbchat::object::User;
use stblib::stbchat::packet::{ClientPacket, ServerPacket};
use stblib::colors::{BOLD, C_RESET, GRAY, RED, YELLOW};

use crate::system_core::log::log_parser;
use crate::system_core::internals::{MessageToClient, MessageToServer};
use crate::system_core::string::StbString;
use crate::system_core::server_core::{remove_hooks_by_user, STATUS};
use crate::constants::log_messages::{CLIENT_KICKED, USER_LEFT};
use crate::global::{LOGGER, MESSAGE_VERIFICATOR};
use crate::security::verification::MessageAction;
use crate::system_core::status::Status;


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
                if matches!(e.downcast_ref::<std::io::Error>().map(std::io::Error::kind), Some(ErrorKind::UnexpectedEof)) {
                    match tx.send(MessageToServer::Broadcast {
                        content: format!("{GRAY}{BOLD}-->{C_RESET} {}{}{YELLOW}{BOLD} left the chat room!{C_RESET}", user.role_color, user.username)
                    }).await {
                        Ok(..) => (),
                        Err(err) => {
                            LOGGER.warning(format!("Unexpected network error: {err}"));
                            return
                        }
                    }

                    tx.send(MessageToServer::RemoveMe {
                        username: user.username.clone()
                    }).await.unwrap();
                    LOGGER.info(log_parser(USER_LEFT, &[&user.username, &peer_addr]));
                    remove_hooks_by_user(user).await;
                    return;
                }
                
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

                tx.send(MessageToServer::RemoveMe {
                    username: user.username.clone()
                }).await.unwrap();
                LOGGER.info(log_parser(USER_LEFT, &[&user.username, &peer_addr]));
                return;
            }

            tx.send(MessageToServer::RunCommand {
                name: parts[0].to_string(),
                args: parts[1..].to_vec(),
            }).await.unwrap();
            
            continue;
        }

        let action = MESSAGE_VERIFICATOR.check_with_user(&content.to_lowercase(), &user).await;

        let content = StbString::from_str(content)
            .check_for_mention()
            .await;
        
        let status = *STATUS.read().await.get_by_name(content.mentioned_user.as_str());
        
        if content.is_mention && content.mentioned_user != user.username && status != Status::DoNotDisturb {
            tx.send(MessageToServer::ClientNotification {
                content: content.clone(),
                bell: false,
                sent_by: user.clone(),
            }).await.unwrap_or_else(|e| {
                LOGGER.error(format!("[S -> {peer_addr}] Failed to send internal packet: {e}"));
            });
        }


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
                }).await.unwrap();

                LOGGER.info(log_parser(
                    CLIENT_KICKED,
                    &[&peer_addr, &"Used blacklisted word"],
                ));
            }
            MessageAction::Hide => {}
            MessageAction::UserMuted => {
                tx.send(MessageToServer::SystemMessage {
                    content: format!("{BOLD}{RED}Sorry, but you were muted by an administrator. \
                    Please contact him/her if you have done nothing wrong, or wait until you are unmuted.{C_RESET}")
                }).await.unwrap();
            }
            MessageAction::Allow => tx.send(MessageToServer::Message { content: content.string }).await.unwrap(),
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
                if let Err(e) = w_stream.write(ClientPacket::SystemMessage {
                        message: content,
                    }).await {
                    LOGGER.error(format!("[S -> {peer_addr}] Failed to send a packet: {e}"));
                    return;
                }
            }
            MessageToClient::Notification { title, username, avatar_url, content, bell} => {
                w_stream.write(ClientPacket::Notification {
                    title,
                    username,
                    avatar_url,
                    content,
                    bell,
                }).await.unwrap_or_else(|e| {
                    LOGGER.error(format!("[S -> {peer_addr}] Failed to send a packet: {e}"));
                });
            }
            MessageToClient::Shutdown => {
                let _ = w_stream.unwrap().shutdown().await;
                return;
            }
        }
    }
}