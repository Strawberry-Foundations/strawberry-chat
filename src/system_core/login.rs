#![allow(clippy::needless_if)]

//! # Login Handler
//! This module handles incoming clients sent over from the client thread
//! - Will handle the full-login

use owo_colors::OwoColorize;
use tokio::net::TcpStream;

use serde_json::Value;

use crate::system_core::deserializer::JsonStreamDeserializer;
use crate::system_core::objects::ClientLoginCredentialsPacket;
use crate::system_core::packet::{EventBackend, SystemMessage};
use crate::system_core::types::LOGIN_EVENT;
use crate::system_core::user::UserObject;

/// Returns None if the client disconnected
pub async fn client_login(stream: &mut TcpStream) -> Option<UserObject> {
    let mut login_packet = EventBackend::new(&LOGIN_EVENT);

    // TODO: replace unwraps with logger errors
    SystemMessage::new(&"Welcome to Strawberry Chat!".bold())
        .write(stream)
        .await
        .unwrap();
    SystemMessage::new(&format!(
        "New here? Type '{}' to register! You want to leave? Type '{}'",
        "Register".magenta(),
        "Exit".magenta()
    ))
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

    Some(UserObject {
        username: client_credentials.username,
        ..Default::default()
    })
}
