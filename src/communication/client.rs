//! # Client Handler
//! This module handles incoming clients sent over from the connection thread
//! - Handles all client-specific things (login, commands, broadcasting)

use std::time::Duration;

use tokio::io::{AsyncWriteExt, split};
use tokio::net::TcpStream;
use tokio::sync::mpsc::{Receiver, Sender};
use tokio::{select, spawn};
use tokio::time::sleep;

use stblib::colors::{BOLD, C_RESET, GRAY, GREEN, RED};
use owo_colors::OwoColorize;

use crate::constants::log_messages::{ADDRESS_LEFT, LOGIN, LOGIN_ERROR, S2C_ERROR};
use crate::global::{CONFIG, LOGGER};
use crate::system_core::log::log_parser;
use crate::system_core::{CORE, login};
use crate::system_core::message::{MessageToClient, MessageToServer};
use crate::system_core::packet::{SystemMessage as SystemMessagePacket, SystemMessage};
use crate::system_core::server_core::get_users_len;
use crate::system_core::types::CRTLCODE_CLIENT_EXIT;
use crate::communication::handlers::{client_incoming, client_outgoing};


pub async fn client_handler(mut client: TcpStream, rx: Receiver<MessageToClient>, tx: Sender<MessageToServer>) {
    let peer_addr = client.peer_addr().unwrap().ip();

    /// # Security: IP-Banning
    /// Security feature for banning specific & static IP addresses
    if CONFIG.security.banned_ips.contains(&peer_addr.to_string()) {
        LOGGER.info(format!("{peer_addr} was disconnection. Reason: IP banned"));

        SystemMessagePacket::new(&format!("{RED}{BOLD}Sorry, you're not allowed to connect to this server.{C_RESET}"))
            .write(&mut client)
            .await
            .unwrap();

        client.shutdown().await.unwrap_or_else(|_| LOGGER.error(S2C_ERROR));

        return
    }

    /// # Core (feat): Client Login
    /// Basic feature to verify that you are you (yes)
    let Some(user) = login::client_login(&mut client).await else {
        tx.send(MessageToServer::RemoveMe).await.unwrap();
        LOGGER.warning(format!("{peer_addr} connection during login"));

        return
    };

    /// # Core (feat): Client Username Verification
    /// Checks if the user is successfully logged in, if not, the value of `user.username` will be `CRTLCODE_CLIENT_EXIT`
    /// This code will check if the username is `CRTLCODE_CLIENT_EXIT`
    if user.username == *CRTLCODE_CLIENT_EXIT {
        SystemMessagePacket::new(&format!("{RED}{BOLD}Invalid username and/or password!{C_RESET}"))
            .write(&mut client)
            .await
            .unwrap();

        LOGGER.info(log_parser(ADDRESS_LEFT, &[&peer_addr]));

        client.shutdown().await.unwrap_or_else(|_| LOGGER.error(S2C_ERROR));

        return
    }

    /// # Core (ext): Client Username Verification
    /// Checks if username is empty in case something gone wrong while logging in
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

    let s2c = spawn(client_outgoing(rx, w_client, peer_addr));
    let c2s = spawn(client_incoming(tx, r_client, peer_addr, user));

    select! {
        _ = c2s => { },
        _ = s2c => { },
    }
}