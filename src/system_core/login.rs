#![allow(clippy::needless_if)]

//! # Login Handler
//! This module handles incoming clients sent over from the client thread
//! - Will handle the full-login

use tokio::net::TcpStream;

use stblib::colors::{BOLD, C_RESET, RED};
use serde_json::Value;
use tokio::io::AsyncWriteExt;

use crate::communication::protocol::JsonStreamDeserializer;
use crate::constants::log_messages::S2C_ERROR;
use crate::database::db::DATABASE;
use crate::global::{CONFIG, LOGGER};
use crate::system_core::objects::{ClientLoginCredentialsPacket, UserAccount};
use crate::system_core::packet::{EventBackend, SystemMessage};
use crate::system_core::types::LOGIN_EVENT;
use crate::system_core::objects::User;

/// Returns None if the client disconnected
pub async fn client_login(stream: &mut TcpStream) -> Option<(UserAccount, User)> {
    let mut login_packet = EventBackend::new(&LOGIN_EVENT);

    // TODO: replace unwraps with logger errors
    SystemMessage::new(&format!("{BOLD}Welcome to {}!{C_RESET}", CONFIG.server.title))
        .write(stream)
        .await
        .unwrap();

    login_packet.write(stream).await.unwrap();

    let mut deserializer = JsonStreamDeserializer::from_read(stream);
    let mut client_credentials = ClientLoginCredentialsPacket::new();

    loop {
        let Ok(msg) = deserializer.next::<Value>().await else {
            continue;
        };

        match msg["packet_type"].as_str() {
            Some("stbchat.event") => match msg["event_type"].as_str() {
                Some("event.login") => {
                    client_credentials.username =
                        msg["credentials"]["username"].as_str().unwrap().to_string();
                    client_credentials.password =
                        msg["credentials"]["password"].as_str().unwrap().to_string();
                    break;
                }
                _ => println!("{msg}"),
            },
            _ => println!("{msg}"),
        }
    }

    let account = DATABASE.check_credentials(&client_credentials.username, &client_credentials.password).await;

    if !account.account_enabled {
        SystemMessage::new(&format!("{RED}{BOLD}Your account was disabled by an administrator.{C_RESET}"))
            .write(deserializer.reader)
            .await
            .unwrap();

        deserializer.reader.shutdown().await.unwrap_or_else(|_| LOGGER.error(S2C_ERROR));
    }

    Some((account.clone(), account.user))
}
