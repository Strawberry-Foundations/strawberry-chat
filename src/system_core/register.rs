use std::net::IpAddr;
use tokio::io::{AsyncWriteExt, WriteHalf};
use tokio::net::TcpStream;

use stblib::stbm::stbchat::net::OutgoingPacketStream;
use stblib::stbm::stbchat::packet::ClientPacket;
use stblib::utilities::contains_whitespace;
use stblib::colors::{BOLD, C_RESET, YELLOW};

use crate::constants::chars::USERNAME_ALLOWED_CHARS;
use crate::constants::log_messages::{DISCONNECTED, S2C_ERROR, WRITE_PACKET_FAIL};
use crate::database::Database;
use crate::database::db::DATABASE;
use crate::global::{CONFIG, LOGGER, MESSAGE_VERIFICATOR};
use crate::security::verification::MessageAction;
use crate::system_core::log::log_parser;
use crate::utilities::is_valid_username;

pub async fn client_register(
    username: String,
    password: String,
    role_color: String,
    w_client: &mut OutgoingPacketStream<WriteHalf<TcpStream>>,
    peer_addr: IpAddr
) {

    /// Check if the username is in blacklisted words
    let action = MESSAGE_VERIFICATOR.check(&username.to_lowercase());

    match action {
        MessageAction::Kick | MessageAction::Hide => {
            w_client.write(ClientPacket::SystemMessage {
                message: format!("{YELLOW}{BOLD}This username is not allowed!{C_RESET}")
            }).await.unwrap_or_else(|_| LOGGER.warning(WRITE_PACKET_FAIL));

            LOGGER.info(log_parser(DISCONNECTED, &[&peer_addr]));
            w_client.inner_mut().shutdown().await.unwrap_or_else(|_| LOGGER.error(format!("{S2C_ERROR} (core::register::#31)")));
        },
        MessageAction::Allow => { }
    }

    /// If username is in this set of blacklisted words, return an error message
    if ["exit", "register", "login", "sid"].contains(&username.as_str()) {
        w_client.write(ClientPacket::SystemMessage {
            message: format!("{YELLOW}{BOLD}This username is not allowed!{C_RESET}")
        }).await.unwrap_or_else(|_| LOGGER.warning(WRITE_PACKET_FAIL));

        LOGGER.info(log_parser(DISCONNECTED, &[&peer_addr]));
        w_client.inner_mut().shutdown().await.unwrap_or_else(|_| LOGGER.error(format!("{S2C_ERROR} (core::register)")));
    }

    /// If username contains whitespaces, return an error message
    if contains_whitespace(&username) {
        w_client.write(ClientPacket::SystemMessage {
            message: format!("{YELLOW}{BOLD}Your username must not contain spaces{C_RESET}")
        }).await.unwrap_or_else(|_| LOGGER.warning(WRITE_PACKET_FAIL));

        LOGGER.info(log_parser(DISCONNECTED, &[&peer_addr]));
        w_client.inner_mut().shutdown().await.unwrap_or_else(|_| LOGGER.error(format!("{S2C_ERROR} (core::register)")));
    }

    /// If username character is not in our charset, return an error message
    if !is_valid_username(&username.as_str(), USERNAME_ALLOWED_CHARS) {
        w_client.write(ClientPacket::SystemMessage {
            message: format!("{YELLOW}{BOLD}Please use only letters, numbers, dots or underscores{C_RESET}")
        }).await.unwrap_or_else(|_| LOGGER.warning(WRITE_PACKET_FAIL));

        LOGGER.info(log_parser(DISCONNECTED, &[&peer_addr]));
        w_client.inner_mut().shutdown().await.unwrap_or_else(|_| LOGGER.error(format!("{S2C_ERROR} (core::register)")));
    }

    /// If username is longer than max_username_length (default: 32) characters, return an error message
    if username.len() > CONFIG.config.max_username_length as usize {
        w_client.write(ClientPacket::SystemMessage {
            message: format!("{YELLOW}{BOLD}Your username is too long{C_RESET}")
        }).await.unwrap_or_else(|_| LOGGER.warning(WRITE_PACKET_FAIL));

        LOGGER.info(log_parser(DISCONNECTED, &[&peer_addr]));
        w_client.inner_mut().shutdown().await.unwrap_or_else(|_| LOGGER.error(format!("{S2C_ERROR} (core::register)")));
    }

    /// Check if username is already taken
    if DATABASE.is_username_taken(&username).await {
        w_client.write(ClientPacket::SystemMessage {
            message: format!("{YELLOW}{BOLD}This username is already in use!{C_RESET}")
        }).await.unwrap_or_else(|_| LOGGER.warning(WRITE_PACKET_FAIL));

        LOGGER.info(log_parser(DISCONNECTED, &[&peer_addr]));
        w_client.inner_mut().shutdown().await.unwrap_or_else(|_| LOGGER.error(format!("{S2C_ERROR} (core::register)")));
    }

    /// If password contains whitespaces, return an error message
    if contains_whitespace(&password) {
        w_client.write(ClientPacket::SystemMessage {
            message: format!("{YELLOW}{BOLD}Your password must not contain spaces{C_RESET}")
        }).await.unwrap_or_else(|_| LOGGER.warning(WRITE_PACKET_FAIL));

        LOGGER.info(log_parser(DISCONNECTED, &[&peer_addr]));
        w_client.inner_mut().shutdown().await.unwrap_or_else(|_| LOGGER.error(format!("{S2C_ERROR} (core::register)")));
    }

    /// If password is longer than max_password_length (default: 256) characters, return an error message
    if password.len() > CONFIG.config.max_password_length as usize {
        w_client.write(ClientPacket::SystemMessage {
            message: format!("{YELLOW}{BOLD}Your password is too long{C_RESET}")
        }).await.unwrap_or_else(|_| LOGGER.warning(WRITE_PACKET_FAIL));

        LOGGER.info(log_parser(DISCONNECTED, &[&peer_addr]));
        w_client.inner_mut().shutdown().await.unwrap_or_else(|_| LOGGER.error(format!("{S2C_ERROR} (core::register)")));
    }

    let user_id = DATABASE.get_next_user_id().await;
    let registered_password = Database::hash_password(password);

    DATABASE.new_user(user_id, username, registered_password, role_color).await;
}