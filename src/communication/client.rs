/// # Client Handler
/// This module handles incoming clients sent over from the connection thread
/// - Handles all client-specific things (login, commands, broadcasting)

use tokio::io::AsyncWriteExt;
use tokio::net::TcpStream;

use stblib::colors::{BOLD, C_RESET, CYAN, RED};
use tokio::sync::mpsc::{UnboundedReceiver, UnboundedSender};

use crate::constants::log_messages::{DISCONNECTED, LOGIN, LOGIN_ERROR, STC_ERROR};
use crate::global::{CONFIG, LOGGER, REGISTRY};
use crate::system_core::log::log_parser;
use crate::system_core::login;
use crate::system_core::message::{MessageToClient, MessageToServer};
use crate::system_core::packet::SystemMessage;
use crate::system_core::types::{CRTLCODE_CLIENT_EXIT, NULL};

pub async fn client_handler(
    mut client: TcpStream,
    incoming: UnboundedReceiver<MessageToClient>,
    outgoing: UnboundedSender<MessageToServer>
) {
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

    let users_len = REGISTRY.users.read().await.len();

    LOGGER.info(log_parser(LOGIN, &[&username, &client_addr]));

    SystemMessage::new(&format!("{BOLD}{CYAN}Welcome back {username}! Nice to see you!{C_RESET}"))
        .write(&mut client)
        .await
        .unwrap();

    let online_users_str =
        if users_len == 1 { format!("there is {users_len} user") }
        else { format!("there are {users_len} users") };

    SystemMessage::new(&format!("{BOLD}{CYAN}Currently there {online_users_str} online. For help use /help!{C_RESET}"))
        .write(&mut client)
        .await
        .unwrap();




}