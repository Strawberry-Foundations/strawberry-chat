use stblib::colors::{BOLD, C_RESET, MAGENTA, RED, RESET};
use stblib::utilities::{ms_sleep};

use crate::system_core::packages::Package;
use crate::system_core::user::{ClientSender, UserObject};

pub async fn client_login(sender: &mut ClientSender) {
    let mut package = Package::new();

    sender.send(package.system.write(&"s")).await;

    let user_object = UserObject {
        username: "julian".to_string(),
        nickname: "Julian The Great".to_string(),
        badge: '👑',
        role_color: format!("{BOLD}{RED}"),
        avatar_url: "https://media.discordapp.net/attachments/874284875618844766/1175912845641265242/WhatsApp_Bild_2023-08-18_um_19.55.41_1.jpg".to_string(),
    };

    sender.send(
        package.user.write(user_object, &"Hi")
    ).await;


    sender.send(format!("{C_RESET}{BOLD}Welcome to Strawberry Chat!{C_RESET}")).await;
    ms_sleep(80);
    sender.send(format!("{C_RESET}{BOLD}New here? Type '{MAGENTA}Register{RESET}' to register! You want to leave? Type '{MAGENTA}Exit{RESET}' {C_RESET}")).await;
}