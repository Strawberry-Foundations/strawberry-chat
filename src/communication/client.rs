//! # Client Handler
//! This module handles incoming clients sent over from the connection thread
//! - Handles all client-specific things (login, commands, broadcasting)

use owo_colors::OwoColorize;
use tokio::io::{AsyncReadExt, AsyncWriteExt, ReadHalf, split, WriteHalf};
use tokio::net::TcpStream;
use tokio::sync::mpsc::{UnboundedReceiver, UnboundedSender};
use tokio::{select, spawn};

use crate::constants::log_messages::{DISCONNECTED, LOGIN, LOGIN_ERROR, STC_ERROR};
use crate::global::{CONFIG, LOGGER};
use crate::system_core::log::log_parser;
use crate::system_core::login;
use crate::system_core::message::{MessageToClient, MessageToServer};
use crate::system_core::packet::{SystemMessage as SystemMessagePacket, SystemMessage, UserMessage as UserMessagePacket};
use crate::system_core::server_core::get_users_len;

// This function should NOT panic!!
async fn client_handler_s2c(mut rx: UnboundedReceiver<MessageToClient>, mut w_stream: WriteHalf<TcpStream>) {
    loop {
        let Some(msg) = rx.recv().await else {
            return;
        };
        match msg {
            // TODO: Replace unwraps with LoggerErrors

            MessageToClient::UserMessage { author, content } => {
                UserMessagePacket::new(author.clone(), &content)
                    .write(&mut w_stream)
                    .await
                    .unwrap();
            },
            MessageToClient::SystemMessage { content } => {
                SystemMessagePacket::new(&content)
                    .write(&mut w_stream)
                    .await
                    .unwrap();
            }
        }
    }
}

async fn client_handler_c2s(tx: UnboundedSender<MessageToServer>, mut r_stream: ReadHalf<TcpStream>) {
    let mut buffer = [0u8; 4096];
    loop {
        // TODO: Replace unwraps with logger errors + RemoveMe

        let n = r_stream.read(&mut buffer).await.unwrap();
        if n == 0 {
            tx.send(MessageToServer::RemoveMe).unwrap();
            return;
        }
        let content = String::from_utf8_lossy(&buffer[..n]).trim().to_string();
        if content.starts_with('/') && content.len() > 1 {
            let parts: Vec<String> = content[1..].split_ascii_whitespace().map(String::from).collect();
            if &parts[0] == "exit" {
                tx.send(MessageToServer::RemoveMe).unwrap();
                return;
            }
            tx.send(MessageToServer::RunCommand {
                name: parts[0].to_string(),
                args: parts[1..].to_vec(),
            }).unwrap();
            continue;
        }

        if content != "[#<keepalive.event.sent>]" { tx.send(MessageToServer::Message { content }).unwrap() };
    }
}

pub async fn client_handler(mut client: TcpStream, rx: UnboundedReceiver<MessageToClient>, tx: UnboundedSender<MessageToServer>) {
    let client_addr = &client.peer_addr().unwrap().ip().clone().to_string();

    if CONFIG.security.banned_ips.contains(client_addr) {
        client.write_all("Sorry, you're not allowed to connect to this server.".red().bold().to_string().as_bytes()).await.expect("");
        client.shutdown().await.unwrap_or_else(|_| LOGGER.error(STC_ERROR));
        LOGGER.info(log_parser(DISCONNECTED, &[&client_addr]));
        return
    }

    let Some(user) = login::client_login(&mut client).await else {
        tx.send(MessageToServer::RemoveMe).unwrap();
        return;
    };


    if user.username.is_empty() {
        LOGGER.error(log_parser(LOGIN_ERROR, &[&client_addr]));
        client.shutdown().await.unwrap_or_else(|_| LOGGER.error(STC_ERROR));
        return
    }

    tx.send(MessageToServer::Authorize { user: user.clone() }).unwrap();


    LOGGER.info(log_parser(LOGIN, &[&user.username, &client_addr]));
    SystemMessage::new(&format!("Welcome back {}! Nice to see you!", user.username).bold().cyan())
        .write(&mut client)
        .await
        .unwrap();

    let users_len = get_users_len().await;
    let online_users_str =
        if users_len == 1 { format!("is {users_len} user") }
        else { format!("are {users_len} users") };

    SystemMessage::new(&format!("Currently there {online_users_str} online. For help use /help!").bold().cyan())
        .write(&mut client)
        .await
        .unwrap();

    let (r_client, w_client) = split(client);
    let s2c = spawn(client_handler_s2c(rx, w_client));
    let c2s = spawn(client_handler_c2s(tx, r_client));
    select! {
        _ = s2c => println!("S->C to {client_addr} closed - that should not have happened, oops!"),
        _ = c2s => println!("C->S to {client_addr} closed"),
    }
}