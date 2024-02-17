#![allow(clippy::needless_if)]

//! # Login Handler
//! This module handles incoming clients sent over from the client thread
//! - Will handle the full-login

use std::net::IpAddr;

use tokio::net::TcpStream;
use tokio::io::{AsyncWriteExt, ReadHalf, WriteHalf};

use stblib::stbm::stbchat::net::{IncomingPacketStream, OutgoingPacketStream};
use stblib::stbm::stbchat::object::{User, Message};
use stblib::stbm::stbchat::packet::{ClientsidePacket, ServersidePacket};
use stblib::colors::{BOLD, C_RESET, RED, YELLOW};

use crate::constants::log_messages::{ADDRESS_LEFT, DISCONNECTED, S2C_ERROR};
use crate::database::db::DATABASE;
use crate::global::{CONFIG, LOGGER};
use crate::system_core::log::log_parser;
use crate::system_core::objects::UserAccount;
use crate::system_core::server_core::get_online_usernames;

/// Returns None if the client disconnected
pub async fn client_login(w_client: &mut OutgoingPacketStream<WriteHalf<TcpStream>>,
    r_client: &mut IncomingPacketStream<ReadHalf<TcpStream>>,
    peer_addr: IpAddr
) -> Option<(UserAccount, User)> {
    // TODO: replace unwraps with logger errors
    w_client.write(
        ClientsidePacket::SystemMessage {
            message: Message::new(format!("{BOLD}Welcome to {}!{C_RESET}", CONFIG.server.title))
        }
    ).await.expect("Failed to write packet");

    let creds;
    loop {
        let Ok(packet) = r_client.read::<ServersidePacket>().await else {
            println!("Failed to read packet");
            return None;
        };

        match packet {
            ServersidePacket::Login { username, password } => {
                creds = (username, password);
                break;
            }
            ServersidePacket::Message { .. } => continue,
        };
    }
    println!("creds: {} :: {}", creds.0, creds.1);
    let (mut account, login_success) = DATABASE.check_credentials(&creds.0, &creds.1).await;

    if !login_success {
        w_client.write(
            ClientsidePacket::SystemMessage {
                message: Message::new(format!("{RED}{BOLD}Invalid username and/or password!{C_RESET}"))
            }
        ).await.expect("Failed to write packet");

        LOGGER.info(log_parser(ADDRESS_LEFT, &[&peer_addr]));

        w_client.inner_mut().shutdown().await.unwrap_or_else(|_| LOGGER.error(format!("{S2C_ERROR} (core::login::#72)")));

        account.ok = false;
    }

    if !account.account_enabled && login_success {
        w_client.write(
            ClientsidePacket::SystemMessage {
                message: Message::new(format!("{RED}{BOLD}Your account was disabled by an administrator.{C_RESET}"))
            }
        ).await.expect("Failed to write packet");
        LOGGER.info(log_parser(DISCONNECTED, &[&peer_addr]));

        w_client.inner_mut().shutdown().await.unwrap_or_else(|_| LOGGER.error(format!("{S2C_ERROR} (core::login::#85)")));

        account.ok = false;
    }

    if !CONFIG.flags.enable_queue
        && CONFIG.config.max_users != -1
        && i16::try_from(get_online_usernames().await.len()).unwrap_or(CONFIG.config.max_users) >= CONFIG.config.max_users {

        w_client.write(
            ClientsidePacket::SystemMessage {
                message: Message::new(format!("{YELLOW}{BOLD}Sorry, Server is full!{C_RESET}"))
            }
        ).await.expect("Failed to write packet");

        LOGGER.info(log_parser(DISCONNECTED, &[&peer_addr]));

        w_client.inner_mut().shutdown().await.unwrap_or_else(|_| LOGGER.error(format!("{S2C_ERROR} (core::login::#101)")));

        account.ok = false;
    }
    else if CONFIG.config.max_users != -1
        && i16::try_from(get_online_usernames().await.len()).unwrap_or(CONFIG.config.max_users) >= CONFIG.config.max_users {
        w_client.write(
            ClientsidePacket::SystemMessage {
                message: Message::new(format!("{YELLOW}{BOLD}Queue is currently not implemented - Server is full!{C_RESET}"))
            }
        ).await.expect("Failed to write packet");

        LOGGER.info(log_parser(DISCONNECTED, &[&peer_addr]));

        w_client.inner_mut().shutdown().await.unwrap_or_else(|_| LOGGER.error(format!("{S2C_ERROR} (core::login::#115)")));

        account.ok = false;
    }

    Some((account.clone(), account.user))
}