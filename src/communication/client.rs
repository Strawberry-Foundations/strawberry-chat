//! # Client Handler
//! This module handles incoming clients sent over from the connection thread
//! - Handles all client-specific things (login, commands, broadcasting)

use std::net::IpAddr;
use std::time::Duration;

use tokio::io::{AsyncReadExt, AsyncWriteExt, ReadHalf, split, WriteHalf};
use tokio::net::TcpStream;
use tokio::sync::mpsc::{Receiver, Sender};
use tokio::{select, spawn};
use tokio::time::sleep;

use stblib::colors::{BOLD, C_RESET, GRAY, GREEN, RED};
use owo_colors::OwoColorize;

use crate::security::automod::MessageAction;
use crate::constants::log_messages::{ADDRESS_LEFT, CLIENT_KICKED, DISCONNECTED, LOGIN, LOGIN_ERROR, S2C_ERROR};
use crate::global::{CONFIG, LOGGER, MESSAGE_VERIFICATOR};
use crate::system_core::log::log_parser;
use crate::system_core::{CORE, login};
use crate::system_core::message::{MessageToClient, MessageToServer};
use crate::system_core::packet::{SystemMessage as SystemMessagePacket, SystemMessage, UserMessage as UserMessagePacket};
use crate::system_core::server_core::get_users_len;
use crate::system_core::types::CRTLCODE_CLIENT_EXIT;

async fn client_handler_s2c(mut rx: Receiver<MessageToClient>, mut w_stream: WriteHalf<TcpStream>, peer_addr: IpAddr) {
    loop {
        let Some(msg) = rx.recv().await else {
            return;
        };
        match msg {
            MessageToClient::UserMessage { author, content } => {
                if let Err(e) = UserMessagePacket::new(author.clone(), &content).write(&mut w_stream).await {
                    LOGGER.error(format!("[S -> {peer_addr}] Failed to send a packet: {e}"));
                    return;
                }
            },
            MessageToClient::SystemMessage { content } => {
                if let Err(e) = SystemMessagePacket::new(&content).write(&mut w_stream).await {
                    LOGGER.error(format!("[S -> {peer_addr}] Failed to send a packet: {e}"));
                    return;
                }
            },
            MessageToClient::Shutdown => { let _ = w_stream.shutdown().await; },
        }
    }
}

async fn client_handler_c2s(tx: Sender<MessageToServer>, mut r_stream: ReadHalf<TcpStream>, peer_addr: IpAddr) {
    let mut buffer = [0u8; 4096];
    loop {
        // TODO: Replace unwraps with logger errors + RemoveMe

        let Ok(n) = r_stream.read(&mut buffer).await else { return };
        if n == 0 {
            let _ = tx.send(MessageToServer::RemoveMe).await;
            return;
        }

        let content = String::from_utf8_lossy(&buffer[..n]).trim().to_string();

        if content.starts_with('/') && content.len() > 1 {
            let parts: Vec<String> = content[1..].split_ascii_whitespace().map(String::from).collect();

            if &parts[0] == "exit" {
                tx.send(MessageToServer::RemoveMe).await.unwrap();
                LOGGER.info(format!("[{peer_addr} -> S] Client exited using /exit"));
                return;
            }

            tx.send(MessageToServer::RunCommand {
                name: parts[0].to_string(),
                args: parts[1..].to_vec(),
            }).await.unwrap();
            continue;
        }

        let action = MESSAGE_VERIFICATOR.check(&content.to_lowercase());

        match action {
            MessageAction::Kick => {
                tx.send(MessageToServer::ClientDisconnect {
                    reason: "Please be friendlier in the chat. Rejoin when you feel ready!".yellow().bold().to_string()
                }).await.unwrap();

                LOGGER.info(log_parser(CLIENT_KICKED, &[&peer_addr, &"Used blacklisted word"]));
            },
            MessageAction::Hide => {},
            MessageAction::Allow => tx.send(MessageToServer::Message { content }).await.unwrap(),
        }
    }
}

pub async fn client_handler(mut client: TcpStream, rx: Receiver<MessageToClient>, tx: Sender<MessageToServer>) {
    let peer_addr = client.peer_addr().unwrap().ip();

    if CONFIG.security.banned_ips.contains(&peer_addr.to_string()) {
        LOGGER.info(format!("[{peer_addr}] Client was disconnection. Reason: IP banned"));
        client.write_all("Sorry, you're not allowed to connect to this server.".red().bold().to_string().as_bytes()).await.expect("");
        client.shutdown().await.unwrap_or_else(|_| LOGGER.error(S2C_ERROR));
        LOGGER.info(log_parser(DISCONNECTED, &[&peer_addr]));
        return
    }

    let Some(user) = login::client_login(&mut client).await else {
        tx.send(MessageToServer::RemoveMe).await.unwrap();
        LOGGER.warning(format!("[{peer_addr}] Client connection during login"));
        return;
    };

    if user.username == *CRTLCODE_CLIENT_EXIT {
        SystemMessagePacket::new(&format!("{RED}{BOLD}Invalid username and/or password!{C_RESET}"))
            .write(&mut client)
            .await
            .unwrap();

        LOGGER.info(log_parser(ADDRESS_LEFT, &[&peer_addr]));

        client.shutdown().await.unwrap_or_else(|_| LOGGER.error(S2C_ERROR));
        return
    }

    if user.username.is_empty() {
        LOGGER.error(log_parser(LOGIN_ERROR, &[&peer_addr]));
        client.shutdown().await.unwrap_or_else(|_| LOGGER.error(S2C_ERROR));
        return
    }

    tx.send(MessageToServer::Authorize { user: user.clone() }).await.unwrap();
    sleep(Duration::from_millis(110)).await;

    LOGGER.info(log_parser(LOGIN, &[&user.username, &peer_addr]));
    SystemMessage::new(&format!("Welcome back {}! Nice to see you!", user.username).bold().cyan())
        .write(&mut client)
        .await
        .unwrap();

    CORE.write().await.add_connection();

    let users_len = get_users_len().await;
    let online_users_str =
        if users_len == 1 { format!("is {users_len} user") }
        else { format!("are {users_len} users") };

    SystemMessage::new(&format!("Currently there {online_users_str} online. For help use /help!").bold().cyan())
        .write(&mut client)
        .await
        .unwrap();

    tx.send(MessageToServer::Broadcast {
        content: format!("{GRAY}{BOLD}-->{C_RESET} {}{}{GREEN}{BOLD} has joined the chat room!{C_RESET}", user.role_color, user.username)
    }).await.unwrap();

    let (r_client, w_client) = split(client);
    let s2c = spawn(client_handler_s2c(rx, w_client, peer_addr));
    let c2s = spawn(client_handler_c2s(tx, r_client, peer_addr));
    select! {
        _ = c2s => LOGGER.info(log_parser(ADDRESS_LEFT, &[&peer_addr])),
        _ = s2c => LOGGER.info(log_parser(ADDRESS_LEFT, &[&peer_addr])),
    }
}