use stblib::colors::{BOLD, C_RESET, MAGENTA, RESET};
use stblib::utilities::{ms_sleep};
use crate::system_core::packages::Package;
use crate::system_core::user::ClientSender;

pub async fn client_login(sender: &mut ClientSender) {
    let mut package = Package::new();

    sender.send(package.system.write("s")).await;

    sender.send(format!("{C_RESET}{BOLD}Welcome to Strawberry Chat!{C_RESET}")).await;
    ms_sleep(80);
    sender.send(format!("{C_RESET}{BOLD}New here? Type '{MAGENTA}Register{RESET}' to register! You want to leave? Type '{MAGENTA}Exit{RESET}' {C_RESET}")).await;
}