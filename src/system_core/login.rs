use stblib::colors::{BOLD, C_RESET, MAGENTA, RED, RESET};

use crate::system_core::packages::{EventBackend, Package};
use crate::system_core::types::LOGIN_EVENT;
use crate::system_core::user::{ClientSender, UserObject};

pub async fn client_login(sender: &mut ClientSender) {
    let mut package = Package::new();
    let mut login_package = EventBackend::new_predefined(&LOGIN_EVENT);

    sender.send(package.system.write(&format!("{C_RESET}{BOLD}Welcome to Strawberry Chat!{C_RESET}"))).await;
    sender.send(package.system.write(&format!("{C_RESET}{BOLD}New here? Type '{MAGENTA}Register{RESET}' to register! You want to leave? Type '{MAGENTA}Exit{RESET}' {C_RESET}"))).await;
    sender.send(login_package.push()).await;

    let user_object = UserObject {
        username: "julian".to_string(),
        nickname: "Julian The Great".to_string(),
        badge: '👑',
        role_color: format!("{BOLD}{RED}"),
        avatar_url: "https://media.discordapp.net/attachments/874284875618844766/1175912845641265242/WhatsApp_Bild_2023-08-18_um_19.55.41_1.jpg".to_string(),
    };

    sender.send(package.user.write(user_object, &"Hi")).await;
}