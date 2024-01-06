//! # Client Handler
//! This module handles incoming clients sent over from the connection thread
//! - Handles all client-specific things (login, commands, broadcasting)

use std::time::Duration;
use tokio::io::{AsyncWriteExt, split};
use tokio::net::TcpStream;
use tokio::sync::mpsc::{UnboundedReceiver, UnboundedSender};

use stblib::colors::{BOLD, C_RESET, CYAN, RED};

use crate::constants::log_messages::{DISCONNECTED, LOGIN, LOGIN_ERROR, STC_ERROR};
use crate::global::{CONFIG, LOGGER};
use crate::system_core::deserializer::JsonStreamDeserializer;
use crate::system_core::log::log_parser;
use crate::system_core::login;
use crate::system_core::message::{MessageToClient, MessageToServer};
use crate::system_core::packet::SystemMessage;
use crate::system_core::server_core::get_users_len;

pub async fn client_handler(mut client: TcpStream, rx: UnboundedReceiver<MessageToClient>, tx: UnboundedSender<MessageToServer>) {
    let client_addr = &client.peer_addr().unwrap().ip().clone().to_string();

    if CONFIG.security.banned_ips.contains(client_addr) {
        client.write_all(format!("{RED}{BOLD}Sorry, you're not allowed to connect to this server.{C_RESET}").as_bytes()).await.expect("");
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

    LOGGER.info(log_parser(LOGIN, &[&user.username, &client_addr]));
    SystemMessage::new(&format!("{BOLD}{CYAN}Welcome back {}! Nice to see you!{C_RESET}", user.username))
        .write(&mut client)
        .await
        .unwrap();

    let users_len = get_users_len().await;
    let online_users_str =
        if users_len == 1 { format!("there is {users_len} user") }
        else { format!("there are {users_len} users") };

    SystemMessage::new(&format!("{BOLD}{CYAN}Currently there {online_users_str} online. For help use /help!{C_RESET}"))
        .write(&mut client)
        .await
        .unwrap();

    let (r_client, w_client) = split(client);

    let mut deser = JsonStreamDeserializer::from_read(r_client);
    loop {
        // C->S
        let msg = tokio::time::timeout(
            Duration::from_millis(10),
            deser.next::<serde_json::Value>()
        ).await;
    }
}