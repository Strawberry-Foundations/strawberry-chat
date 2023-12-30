use std::collections::HashMap;
use std::net::IpAddr;
use stblib::colors::{BOLD, C_RESET, RED};

use stblib::utilities::unix_time;

use tokio::io::AsyncWriteExt;
use tokio::net::TcpListener;
use tokio::spawn;
use crate::communication::client::client_handler;

use crate::global::{CONFIG, LOGGER};
use crate::system_core::log_parser::log_parser;
use crate::system_core::log_messages::{CONNECTED, CONNECTED_RLM, CONNECTION_ERROR, RATELIMIT_REMOVED, REACHED_CON_LIMIT};

pub async fn connection_handler(socket: TcpListener) {
    let mut ignore_list: HashMap<IpAddr, u64> = HashMap::new();
    let mut connection_counter: HashMap<IpAddr, u8> = HashMap::new();

    loop {
        let Ok((mut client, _)) = socket.accept().await else {
                LOGGER.error(CONNECTION_ERROR);
                continue;
            };

        let client_addr= client.peer_addr().unwrap().ip();

        if CONFIG.networking.ratelimit {
            if ignore_list.contains_key(&client_addr) {
                if !(unix_time() - ignore_list.get(&client_addr).unwrap()) > u64::from(CONFIG.networking.ratelimit_timeout) {
                    LOGGER.info(log_parser(CONNECTED_RLM, &[&client_addr.to_string(),] ));

                    client.write_all(
                        format!("{RED}{BOLD}You have been ratelimited due to spam activity. Please try again later{C_RESET}").as_bytes()
                    ).await.unwrap_or_else(|_| {
                        LOGGER.warning("warning");
                    });
                }
                else {
                    LOGGER.info(log_parser(RATELIMIT_REMOVED, &[&client_addr.to_string()]));
                }
            }
            else if connection_counter.contains_key(&client_addr) {
                if connection_counter[&client_addr] >= 10 {
                    LOGGER.warning(log_parser(REACHED_CON_LIMIT, &[&client_addr.to_string()]));
                    ignore_list.insert(client_addr, unix_time());
                }
                else {
                    LOGGER.info(log_parser(CONNECTED, &[&client_addr.to_string()]));
                    *connection_counter.entry(client_addr).or_insert(0) += 1;
                }
            }
        }
        else {
            LOGGER.info(log_parser(CONNECTED, &[&client_addr.to_string()]));
            spawn(client_handler()).await.expect("");
        }

        client.write_all(client.peer_addr().unwrap().to_string().as_bytes()).await.unwrap_or_else(|_| {
           LOGGER.error("");
        });
    }
}