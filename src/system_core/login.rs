use stblib::colors::{BOLD, C_RESET, MAGENTA, RED, RESET};
use tokio::io::AsyncReadExt;
use tokio::net::TcpStream;

use crate::system_core::packet::{EventBackend, SystemMessage, UserMessage};
use crate::system_core::types::LOGIN_EVENT;
use crate::system_core::user::UserObject;

pub async fn client_login(stream: &mut TcpStream) -> String {
    let mut login_packet = EventBackend::new(&LOGIN_EVENT);

    // TODO: replace unwraps with logger errors
    SystemMessage::new(&format!("{C_RESET}{BOLD}Welcome to Strawberry Chat!{C_RESET}"))
        .write(stream)
        .await
        .unwrap();
    SystemMessage::new(&format!("{C_RESET}{BOLD}New here? Type '{MAGENTA}Register{RESET}' to register! You want to leave? Type '{MAGENTA}Exit{RESET}' {C_RESET}"))
        .write(stream)
        .await
        .unwrap();

    login_packet.write(stream).await.unwrap();

    let user_object = UserObject {
        username: "julian".to_string(),
        nickname: "Julian The Great".to_string(),
        badge: '👑',
        role_color: format!("{BOLD}{RED}"),
        avatar_url: "https://media.discordapp.net/attachments/874284875618844766/1175912845641265242/WhatsApp_Bild_2023-08-18_um_19.55.41_1.jpg".to_string(),
    };

    UserMessage::new(user_object, &"Hi :)")
        .write(stream)
        .await
        .unwrap();

    let mut buffer = [0; 1024];

    let n = stream.read(&mut buffer).await.unwrap_or({
        0
    });

    String::from_utf8_lossy(&buffer[0..n]).to_string()
}