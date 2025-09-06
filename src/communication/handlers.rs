use std::io::ErrorKind;
use std::net::IpAddr;

use tokio::io::{AsyncWriteExt, ReadHalf, WriteHalf};
use tokio::net::TcpStream;
use tokio::sync::mpsc::{Receiver, Sender};

use libstrawberry::stbchat::net::{IncomingPacketStream, OutgoingPacketStream};
use libstrawberry::stbchat::object::User;
use libstrawberry::stbchat::packet::{ClientPacket, ServerPacket};
use libstrawberry::colors::{BOLD, C_RESET, GRAY, RED, YELLOW};

use crate::system_core::log::log_parser;
use crate::system_core::internals::{MessageToClient, MessageToServer};
use crate::system_core::string::StbString;
use crate::system_core::server_core::{remove_hooks_by_user, STATUS};
use crate::constants::log_messages::{CLIENT_KICKED, USER_LEFT};
use crate::database::DATABASE;
use crate::global::{CONFIG, LOGGER, MESSAGE_VERIFICATOR};
use crate::security::verification::MessageAction;
use crate::system_core::status::Status;

async fn handle_client_disconnect(
    tx: &Sender<MessageToServer>,
    user: &User,
    peer_addr: IpAddr,
) -> Result<(), tokio::sync::mpsc::error::SendError<MessageToServer>> {
    tx.send(MessageToServer::Broadcast {
        content: format!("{GRAY}{BOLD}-->{C_RESET} {}{}{YELLOW}{BOLD} left the chat room!{C_RESET}", user.role_color, user.username)
    }).await?;

    tx.send(MessageToServer::RemoveMe {
        username: Some(user.username.clone())
    }).await?;
    
    LOGGER.info(log_parser(USER_LEFT, &[&user.username, &peer_addr]));
    remove_hooks_by_user(user.clone()).await;
    Ok(())
}

async fn handle_command(
    tx: &Sender<MessageToServer>,
    user: &User,
    peer_addr: IpAddr,
    content: &str,
) -> Result<bool, tokio::sync::mpsc::error::SendError<MessageToServer>> {
    if !content.starts_with('/') || content.len() <= 1 {
        return Ok(false);
    }

    let parts: Vec<String> = content[1..]
        .split_ascii_whitespace()
        .map(String::from)
        .collect();

    if &parts[0] == "exit" {
        handle_client_disconnect(tx, user, peer_addr).await?;
        return Ok(true);
    }

    tx.send(MessageToServer::RunCommand {
        name: parts[0].to_string(),
        args: parts[1..].to_vec(),
    }).await?;
    
    Ok(true)
}

async fn handle_message_action(
    tx: &Sender<MessageToServer>,
    action: MessageAction,
    user: &User,
    peer_addr: IpAddr,
    content: &StbString,
) -> Result<(), tokio::sync::mpsc::error::SendError<MessageToServer>> {
    match action {
        MessageAction::Kick => {
            tx.send(MessageToServer::Broadcast {
                content: format!("{GRAY}{BOLD}-->{C_RESET} {}{}{YELLOW}{BOLD} left the chat room!{C_RESET}", user.role_color, user.username)
            }).await?;

            tx.send(MessageToServer::ClientDisconnect {
                reason: format!("{YELLOW}{BOLD}Please be friendlier in the chat. Rejoin when you feel ready!{C_RESET}"),
            }).await?;

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
            }).await?;
        }
        MessageAction::TooLong => {
            tx.send(MessageToServer::SystemMessage {
                content: format!("{BOLD}{YELLOW}Your message is too long ({}/{}){C_RESET}", content.len(), CONFIG.config.max_message_length)
            }).await?;
        }
        MessageAction::Allow => {
            tx.send(MessageToServer::Message { content: content.string.clone() }).await?;
        }
    }
    Ok(())
}

async fn handle_mention_notification(
    tx: &Sender<MessageToServer>,
    content: &StbString,
    user: &User,
    peer_addr: IpAddr,
) {
    if !content.is_mention || content.mentioned_user == user.username {
        return;
    }

    let status = *STATUS.read().await.get_by_name(content.mentioned_user.as_str());
    if status == Status::DoNotDisturb {
        return;
    }

    let blocked_users_recipient: String = DATABASE.get_blocked_from_user(content.mentioned_user.as_str()).await;

    if !blocked_users_recipient.split(',').any(|x| x == user.username) {
        tx.send(MessageToServer::ClientNotification {
            content: content.clone(),
            bell: false,
            sent_by: user.clone(),
        }).await.unwrap_or_else(|e| {
            LOGGER.error(format!("[S -> {peer_addr}] Failed to send internal packet: {e}"));
        });
    }
}

pub async fn client_incoming(
    tx: Sender<MessageToServer>,
    mut r_stream: IncomingPacketStream<ReadHalf<TcpStream>>,
    peer_addr: IpAddr,
    user: User,
) {
    loop {
        let msg = match r_stream.read::<ServerPacket>().await {
            Ok(ServerPacket::Message { message }) => message,
            Err(e) => {
                if matches!(e.downcast_ref::<std::io::Error>().map(std::io::Error::kind), Some(ErrorKind::UnexpectedEof)) {
                    if let Err(err) = handle_client_disconnect(&tx, &user, peer_addr).await {
                        LOGGER.warning(format!("Unexpected network error: {err}"));
                    }
                    return;
                }
                
                LOGGER.warning(format!("Failed to read packet, received from {peer_addr}: {e}"));
                break;
            }
            _ => continue,
        };

        let content = strip_ansi_escapes::strip_str(msg);

        // Handle commands
        match handle_command(&tx, &user, peer_addr, &content).await {
            Ok(true) => return, // Command was processed and client should disconnect
            Ok(false) => {}, // Not a command, continue processing as message
            Err(e) => {
                LOGGER.error(format!("Failed to handle command: {e}"));
                break;
            }
        }

        let action = MESSAGE_VERIFICATOR.check_with_user(&content.to_lowercase(), &user).await;

        let content = StbString::from_str(content)
            .check_for_mention()
            .await;

        // Handle mention notifications
        handle_mention_notification(&tx, &content, &user, peer_addr).await;

        // Handle message action (kick, mute, allow, etc.)
        if let Err(e) = handle_message_action(&tx, action, &user, peer_addr, &content).await {
            LOGGER.error(format!("Failed to handle message action: {e}"));
            break;
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