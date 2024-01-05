use tokio::io::AsyncWriteExt;
use tokio::net::TcpStream;

use stblib::colors::{BOLD, C_RESET, RED};

use crate::constants::log_messages::{DISCONNECTED, LOGIN, LOGIN_ERROR, STC_ERROR};
use crate::global::{CONFIG, LOGGER};
use crate::system_core::log::log_parser;
use crate::system_core::login;
use crate::system_core::types::{CRTLCODE_CLIENT_EXIT, NULL};

pub async fn client_handler(mut client: TcpStream) {
    let client_addr = &client.peer_addr().unwrap().ip().clone().to_string();

    if CONFIG.security.banned_ips.contains(client_addr) {
        client.write_all(format!("{RED}{BOLD}Sorry, you're not allowed to connect to this server.{C_RESET}").as_bytes()).await.expect("");
        client.shutdown().await.unwrap_or_else(|_| LOGGER.error(STC_ERROR));
        LOGGER.info(log_parser(DISCONNECTED, &[&client_addr]));
        return
    }


    let username = login::client_login(&mut client).await;

    if username == NULL || username == CRTLCODE_CLIENT_EXIT {
        LOGGER.error(log_parser(LOGIN_ERROR, &[&client_addr]));
        client.shutdown().await.unwrap_or_else(|_| LOGGER.error(STC_ERROR));
        return
    }

    LOGGER.info(log_parser(LOGIN, &[&username, &client_addr]));
}