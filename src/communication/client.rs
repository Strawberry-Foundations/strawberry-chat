//! # Client Handler
//! This module handles incoming clients sent over from the connection thread
//! - Handles all client-specific things (login, commands, broadcasting)

use std::time::Duration;

use tokio::io::{AsyncWriteExt, split};
use tokio::net::TcpStream;
use tokio::sync::mpsc::{Receiver, Sender};
use tokio::{select, spawn};
use tokio::time::sleep;

use stblib::stbchat::net::{IncomingPacketStream, OutgoingPacketStream};
use stblib::stbchat::packet::ClientPacket;
use stblib::colors::{BOLD, C_RESET, GRAY, GREEN, RED};

use owo_colors::OwoColorize;

use crate::system_core::server_core::get_users_len;
use crate::system_core::log::log_parser;
use crate::system_core::login;
use crate::system_core::internals::{MessageToClient, MessageToServer};
use crate::communication::handlers::{client_incoming, client_outgoing};
use crate::global::{CONFIG, LOGGER};
use crate::constants::types::CRTLCODE_CLIENT_EXIT;
use crate::constants::log_messages::{ADDRESS_LEFT, LOGIN, LOGIN_ERROR, S2C_ERROR, WRITE_PACKET_FAIL};


pub async fn client_handler(client: TcpStream, rx: Receiver<MessageToClient>, tx: Sender<MessageToServer>) {
    let peer_addr = client.peer_addr().unwrap().ip();

    let (r_client, w_client) = split(client);
    
    let mut r_client = IncomingPacketStream::wrap(r_client);
    let mut w_client = OutgoingPacketStream::wrap(w_client);

    /// # Security: IP-Banning
    /// Security feature for banning specific & static IP addresses
    if CONFIG.security.banned_ips.contains(&peer_addr.to_string()) {
        LOGGER.info(format!("{peer_addr} was disconnection. Reason: IP banned"));

        w_client.write(
            ClientPacket::SystemMessage {
                message: format!("{RED}{BOLD}Sorry, you're not allowed to connect to this server.{C_RESET}")
            }
        ).await.unwrap_or_else(|_| LOGGER.warning(WRITE_PACKET_FAIL));

        w_client.inner_mut().shutdown().await.unwrap_or_else(|_| LOGGER.error(format!("{S2C_ERROR} (com::client::#40)")));

        return
    }

    /// # Core (feat): Client Login
    /// Basic feature to verify that you are you (yes)
    let Some((account, user)) = login::client_login(&mut w_client, &mut r_client, peer_addr).await else {
        tx.send(MessageToServer::RemoveMe).await.unwrap(); // <--- stbbugs::20240202--1: Calls Exception when leaving stbchat while login screen

        tokio::time::sleep(Duration::from_millis(140)).await;

        LOGGER.warning(format!("Error logging in {peer_addr}, connection to the client was disconnected"));

        return
    };

    /// # Core (feat): Account Ok Status
    /// Checks if the account is after all the login things in a "good" status
    if !account.account_enabled || !account.ok {
        return
    }

    /// # Core (feat): Client Username Verification
    /// Checks if the user is successfully logged in, if not, the value of `user.username` will be `CRTLCODE_CLIENT_EXIT`
    /// This code will check if the username is `CRTLCODE_CLIENT_EXIT`
    if user.username == *CRTLCODE_CLIENT_EXIT{
        w_client.write(
            ClientPacket::SystemMessage {
                message: format!("{RED}{BOLD}Invalid username and/or password!{C_RESET}")
            }
        ).await.unwrap_or_else(|_| LOGGER.warning(WRITE_PACKET_FAIL));

        LOGGER.info(log_parser(ADDRESS_LEFT, &[&peer_addr]));

        w_client.inner_mut().shutdown().await.unwrap_or_else(|_| LOGGER.error(format!("{S2C_ERROR} (com::client::#71)")));

        return
    }

    /// # Core (ext): Client Username Verification
    /// Checks if username is empty in case something gone wrong while logging in
    if user.username.is_empty() {
        LOGGER.error(log_parser(LOGIN_ERROR, &[&peer_addr]));
        w_client.inner_mut().shutdown().await.unwrap_or_else(|_| LOGGER.error(format!("{S2C_ERROR} (com::client::#80)")));

        return
    }

    tx.send(MessageToServer::Authorize { user: user.clone() }).await.unwrap();
    sleep(Duration::from_millis(110)).await;

    LOGGER.info(log_parser(LOGIN, &[&user.username, &peer_addr]));

    w_client.write(
        ClientPacket::SystemMessage {
            message: format!("Welcome back {}! Nice to see you!", user.username).bold().cyan().to_string()
        }
    ).await.unwrap_or_else(|_| LOGGER.warning(WRITE_PACKET_FAIL));
    
    let users_len = get_users_len().await;
    let online_users_str =
        if users_len == 1 { format!("is {users_len} user") }
        else { format!("are {users_len} users") };

    w_client.write(
        ClientPacket::SystemMessage {
            message: format!("Currently there {online_users_str} online. For help use /help!").bold().cyan().to_string()
        }
    ).await.unwrap_or_else(|_| LOGGER.warning(WRITE_PACKET_FAIL));

    tx.send(MessageToServer::Broadcast {
        content: format!("{GRAY}{BOLD}-->{C_RESET} {}{}{GREEN}{BOLD} has joined the chat room!{C_RESET}", user.role_color, user.username)
    }).await.unwrap();

    let s2c = spawn(client_outgoing(rx, w_client, peer_addr));
    let c2s = spawn(client_incoming(tx, r_client, peer_addr, user));

    select! {
        _ = c2s => { },
        _ = s2c => { },
    }
}