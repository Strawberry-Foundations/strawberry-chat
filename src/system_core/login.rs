#![allow(clippy::needless_if)]

//! # Login Handler
//! This module handles incoming clients sent over from the client thread
//! - Will handle the full-login

use std::net::IpAddr;

use tokio::net::TcpStream;
use tokio::io::{AsyncWriteExt, ReadHalf, WriteHalf};

use stblib::stbchat::net::{IncomingPacketStream, OutgoingPacketStream};
use stblib::stbchat::object::User;
use stblib::stbchat::packet::{ClientPacket, ServerPacket};
use stblib::colors::{BOLD, C_RESET, RED, YELLOW};

use crate::system_core::log::log_parser;
use crate::system_core::objects::UserAccount;
use crate::system_core::register::client_register;
use crate::system_core::server_core::get_online_usernames;
use crate::constants::log_messages::{ADDRESS_LEFT, DISCONNECTED, READ_PACKET_FAIL, S2C_ERROR, WRITE_PACKET_FAIL};
use crate::database::DATABASE;
use crate::global::{CONFIG, LOGGER};

/// Returns None if the client disconnected
pub async fn client_login(w_client: &mut OutgoingPacketStream<WriteHalf<TcpStream>>,
    r_client: &mut IncomingPacketStream<ReadHalf<TcpStream>>,
    peer_addr: IpAddr
) -> Option<(UserAccount, User)> {
    // TODO: replace unwraps with logger errors

    w_client.write(ClientPacket::SystemMessage {
        message: format!("{BOLD}Welcome to {}!{C_RESET}", CONFIG.server.name)
    }).await.unwrap_or_else(|_| LOGGER.warning(WRITE_PACKET_FAIL));

    w_client.write(ClientPacket::Event {
        event_type: String::from("event.login")
    }).await.unwrap_or_else(|_| LOGGER.warning(WRITE_PACKET_FAIL));

    let credentials: (String, String);

    loop {
        let Ok(packet) = r_client.read::<ServerPacket>().await else {
            LOGGER.warning(READ_PACKET_FAIL);
            return None;
        };

        match packet {
            ServerPacket::Login { username, password } => {
                credentials = (username, password);
                break;
            }
            ServerPacket::Register { username, password, role_color} => {
                credentials = (username.clone(), password.clone());
                client_register(username, password, role_color, w_client, peer_addr).await;
                break;
            }
            _ => continue,
        };
    }

    w_client.write(ClientPacket::SystemMessage {
        message: format!("{BOLD}Checking your credentials...{C_RESET}")
    }).await.unwrap_or_else(|_| LOGGER.warning(WRITE_PACKET_FAIL));
    
    let mut account = if let Some(account) = DATABASE.check_credentials(&credentials.0, &credentials.1).await {
        account
    } else {
        w_client.write(ClientPacket::SystemMessage {
            message: format!("{RED}{BOLD}Invalid username and/or password!{C_RESET}")
        }).await.unwrap_or_else(|_| LOGGER.warning(WRITE_PACKET_FAIL));

        LOGGER.info(log_parser(ADDRESS_LEFT, &[&peer_addr]));

        w_client.inner_mut().shutdown().await.unwrap_or_else(|_| LOGGER.error(format!("{S2C_ERROR} (core::login::#72)")));

        return None
    };

    if !account.account_enabled {
        w_client.write(ClientPacket::SystemMessage {
            message: format!("{RED}{BOLD}Your account was disabled by an administrator.{C_RESET}")
        }).await.unwrap_or_else(|_| LOGGER.warning(WRITE_PACKET_FAIL));
        
        LOGGER.info(log_parser(DISCONNECTED, &[&peer_addr]));

        w_client.inner_mut().shutdown().await.unwrap_or_else(|_| LOGGER.error(format!("{S2C_ERROR} (core::login::#85)")));

        account.ok = false;
    }

    if !CONFIG.flags.enable_queue
        && CONFIG.config.max_users != -1
        && i16::try_from(get_online_usernames().await.len()).unwrap_or(CONFIG.config.max_users) >= CONFIG.config.max_users {

        w_client.write(
            ClientPacket::SystemMessage {
                message: format!("{YELLOW}{BOLD}Sorry, Server is full!{C_RESET}")
            }
        ).await.unwrap_or_else(|_| LOGGER.warning(WRITE_PACKET_FAIL));

        LOGGER.info(log_parser(DISCONNECTED, &[&peer_addr]));

        w_client.inner_mut().shutdown().await.unwrap_or_else(|_| LOGGER.error(format!("{S2C_ERROR} (core::login::#101)")));

        account.ok = false;
    }
    else if CONFIG.config.max_users != -1
        && i16::try_from(get_online_usernames().await.len()).unwrap_or(CONFIG.config.max_users) >= CONFIG.config.max_users {
        w_client.write(
            ClientPacket::SystemMessage {
                message: format!("{YELLOW}{BOLD}Queue is currently not implemented - Server is full!{C_RESET}")
            }
        ).await.unwrap_or_else(|_| LOGGER.warning(WRITE_PACKET_FAIL));

        LOGGER.info(log_parser(DISCONNECTED, &[&peer_addr]));

        w_client.inner_mut().shutdown().await.unwrap_or_else(|_| LOGGER.error(format!("{S2C_ERROR} (core::login::#115)")));

        account.ok = false;
    }

    Some((account.clone(), account.user))
}