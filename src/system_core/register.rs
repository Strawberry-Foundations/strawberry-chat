use std::net::IpAddr;
use stblib::colors::{BOLD, C_RESET, YELLOW};
use stblib::stbm::stbchat::net::OutgoingPacketStream;
use stblib::stbm::stbchat::packet::ClientPacket;
use stblib::utilities::contains_whitespace;
use tokio::io::{AsyncWriteExt, WriteHalf};
use tokio::net::TcpStream;
use crate::constants::log_messages::{DISCONNECTED, S2C_ERROR, WRITE_PACKET_FAIL};
use crate::global::{LOGGER, MESSAGE_VERIFICATOR};
use crate::security::verification::MessageAction;
use crate::system_core::log::log_parser;

pub async fn client_register(
    username: String,
    password: String,
    role_color: String,
    w_client: &mut OutgoingPacketStream<WriteHalf<TcpStream>>,
    peer_addr: IpAddr
) {
    let action = MESSAGE_VERIFICATOR.check(&username.to_lowercase());

    match action {
        MessageAction::Kick | MessageAction::Hide => {
            w_client.write(ClientPacket::SystemMessage { 
                message: format!("{YELLOW}{BOLD}This username is not allowed!{C_RESET}") 
            }).await.unwrap_or_else(|_| LOGGER.warning(WRITE_PACKET_FAIL));

            LOGGER.info(log_parser(DISCONNECTED, &[&peer_addr]));
            w_client.inner_mut().shutdown().await.unwrap_or_else(|_| LOGGER.error(format!("{S2C_ERROR} (core::login::#85)")));
        },
        MessageAction::Allow => { }
    }

    if contains_whitespace(&username) {
        w_client.write(ClientPacket::SystemMessage {
            message: format!("{YELLOW}{BOLD}Your username must not contain spaces{C_RESET}")
        }).await.unwrap_or_else(|_| LOGGER.warning(WRITE_PACKET_FAIL));

        LOGGER.info(log_parser(DISCONNECTED, &[&peer_addr]));
        w_client.inner_mut().shutdown().await.unwrap_or_else(|_| LOGGER.error(format!("{S2C_ERROR} (core::login::#85)")));
    }
    
    if !
}