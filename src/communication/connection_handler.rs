//! # Connection Handler
//! This module will handle all incoming connections
//! - Accepts incoming connections and then sends them to the client thread after a few checks
//! - Will handle connection rate-limiting
//! - Will NOT handle login & client-specific things

use std::collections::HashMap;
use std::net::IpAddr;

use tokio::io::AsyncWriteExt;
use tokio::net::TcpListener;
use tokio::spawn;

use stblib::utilities::unix_time;
use stblib::colors::{BOLD, C_RESET, RED};
use stblib::stbm::stbchat::net::OutgoingPacketStream;
use stblib::stbm::stbchat::packet::ClientPacket;
use stblib::stbm::stbchat::object::Message;

use crate::communication::client::client_handler;
use crate::global::{CONFIG, LOGGER};
use crate::system_core::log::log_parser;
use crate::constants::log_messages::{CONNECTED, CONNECTED_RLM, CONNECTION_ERROR, RATELIMIT_REMOVED, REACHED_CON_LIMIT, WRITE_PACKET_FAIL, WRITE_STREAM_FAIL};
use crate::system_core::server_core::register_connection;

pub async fn connection_handler(socket: TcpListener) {
    let mut ignore_list: HashMap<IpAddr, u64> = HashMap::new();
    let mut connection_counter: HashMap<IpAddr, u8> = HashMap::new();

    loop {
        let Ok((mut client, _)) = socket.accept().await else {
            LOGGER.error(CONNECTION_ERROR);
            continue;
        };

        let client_addr = match client.peer_addr() {
            Ok(peer_addr) => peer_addr.ip(),
            Err(_) => continue
        };

        if !CONFIG.networking.ratelimit {
            LOGGER.info(log_parser(CONNECTED, &[&client_addr.to_string()]));
            let Ok(peer_addr) = client.peer_addr() else { continue };

            let (tx, rx) = register_connection(peer_addr).await;

            spawn(client_handler(client, rx, tx));
            continue;
        }

        /// # Ratelimit Feature
        /// This feature prevents user from spamming connection streams to the server
        /// - Configurable ratelimit timeout (disallow connection to server for n seconds)
        /// - Stable and secure
        /// - Spam protection is activated from 10 connections
        let mut allow_connection = true;

        // Check if ignore list contains the client's address
        if let std::collections::hash_map::Entry::Vacant(e) = ignore_list.entry(client_addr) {
            // If connection counter of user is higher or equals to 10, disallow connection to the server
            if connection_counter.contains_key(&client_addr) && connection_counter[&client_addr] >= 10 {
                LOGGER.warning(log_parser(REACHED_CON_LIMIT, &[&client_addr.to_string()]));
                e.insert(unix_time());
                allow_connection = false;
            }
            // Else continue connection
            else {
                LOGGER.info(log_parser(CONNECTED, &[&client_addr.to_string()]));
                *connection_counter.entry(client_addr).or_insert(0) += 1;
            }
        } else {
            // Check if user is still in ratelimit timeout (If user is no longer in ratelimit timeout, remove user from the ignore_list
            if (unix_time() - ignore_list.get(&client_addr).unwrap()) > u64::from(CONFIG.networking.ratelimit_timeout) {
                LOGGER.info(log_parser(RATELIMIT_REMOVED, &[&client_addr.to_string()]));

                ignore_list.remove(&client_addr);
                connection_counter.remove(&client_addr);
            }

            // if user is still in ratelimit timeout, send message and close connection
            else {
                LOGGER.info(log_parser(CONNECTED_RLM, &[&client_addr.to_string(), ]));
                let mut s = OutgoingPacketStream::wrap(client);
                s.write(
                    ClientPacket::SystemMessage {
                        message: Message::new(format!("{RED}{BOLD}You have been ratelimited due to spam activity. Please try again later{C_RESET}"))
                    }
                )
                    .await.unwrap_or_else(|_| LOGGER.warning(WRITE_STREAM_FAIL));

                allow_connection = false;
                client = s.unwrap();
            }
        }

        if allow_connection {
            let (tx, rx) = register_connection(client.peer_addr().unwrap()).await;
            spawn(client_handler(client, rx, tx));
        } else {
            client.shutdown().await.unwrap_or(());
        }
    }
}