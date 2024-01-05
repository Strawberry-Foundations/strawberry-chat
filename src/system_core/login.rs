#![allow(clippy::needless_if)]

/// # Login Handler
/// This module handles incoming clients sent over from the client thread
/// - Will handle the full-login

use tokio::net::TcpStream;

use serde_json::{Deserializer, Value};

use stblib::colors::{BOLD, C_RESET, MAGENTA, RED, RESET};

use crate::system_core::objects::ClientLoginCredentialsPacket;
use crate::system_core::packet::{EventBackend, SystemMessage, UserMessage};
use crate::system_core::types::LOGIN_EVENT;
use crate::system_core::user::UserObject;

pub async fn client_login(stream: &mut TcpStream) -> String {
    let std_stream = stream.into_std().unwrap();
    let mut stream = TcpStream::from_std(std_stream.try_clone().unwrap()).unwrap();

    let mut login_packet = EventBackend::new(&LOGIN_EVENT);

    // TODO: replace unwraps with logger errors
    SystemMessage::new(&format!("{C_RESET}{BOLD}Welcome to Strawberry Chat!{C_RESET}"))
        .write(&mut stream)
        .await
        .unwrap();
    SystemMessage::new(&format!("{C_RESET}{BOLD}New here? Type '{MAGENTA}Register{RESET}' to register! You want to leave? Type '{MAGENTA}Exit{RESET}' {C_RESET}"))
        .write(&mut stream)
        .await
        .unwrap();

    login_packet.write(&mut stream).await.unwrap();

    let user_object = UserObject {
        username: "julian".to_string(),
        nickname: "Julian The Great".to_string(),
        badge: '👑',
        role_color: format!("{BOLD}{RED}"),
        avatar_url: "https://media.discordapp.net/attachments/874284875618844766/1175912845641265242/WhatsApp_Bild_2023-08-18_um_19.55.41_1.jpg".to_string(),
    };

    UserMessage::new(user_object, &"Hi :)")
        .write(&mut stream)
        .await
        .unwrap();

    let json_iter = Deserializer::from_reader(std_stream).into_iter::<Value>();
    let mut client_credentials = ClientLoginCredentialsPacket::new();

    for json in json_iter {
        let msg = match json {
            Ok(j) => j,
            Err(e) => {
                eprintln!("Failed to deserialize json: {e}");
                continue
            },
        };

        match msg["packet_type"].as_str() {
            Some("stbchat.event") => {
                match msg["event.login"].as_str() {
                    Some("") => {


                    },
                    _ => { }
                }

            },
            _ => { }

        }
    }

   "".to_string()
}