use tokio::io::AsyncWriteExt;
use tokio::net::TcpStream;

use stblib::colors::{BOLD, C_RESET, RED};

use crate::constants::log_messages::{LOGIN, STC_ERROR};
use crate::global::{CONFIG, LOGGER};
use crate::system_core::log::log_parser;
use crate::system_core::login;

pub async fn client_handler(mut client: TcpStream) {
    if CONFIG.security.banned_ips.contains(&client.peer_addr().unwrap().ip().clone().to_string()) {
        client.write_all(format!("{RED}{BOLD}Sorry, you're not allowed to connect to this server.{C_RESET}").as_bytes()).await.expect("");
        client.shutdown().await.unwrap_or_else(|_| LOGGER.error(STC_ERROR));
        return
    }


    let username = login::client_login(&mut client).await;
    LOGGER.info(log_parser(LOGIN, &[&username,]));
}