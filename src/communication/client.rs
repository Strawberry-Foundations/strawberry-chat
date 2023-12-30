use tokio::io::AsyncWriteExt;
use tokio::net::TcpStream;

use stblib::colors::{BOLD, C_RESET, RED};

use crate::constants::log_messages::STC_ERROR;
use crate::global::{CONFIG, LOGGER};
use crate::system_core::login;
use crate::system_core::user;

pub async fn client_handler(mut client: TcpStream) {
    if CONFIG.security.banned_ips.contains(&client.peer_addr().unwrap().ip().clone().to_string()) {
        client.write_all(format!("{RED}{BOLD}Sorry, you're not allowed to connect to this server.{C_RESET}").as_bytes()).await.expect("");
        client.shutdown().await.unwrap_or_else(|_| LOGGER.error(STC_ERROR));
        return
    }

    let mut sender = user::ClientSender::new(client);

    let _username = login::client_login(&mut sender).await;
}