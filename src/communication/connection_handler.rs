use std::collections::HashMap;
use std::net::IpAddr;
use stblib::colors::{BOLD, C_RESET, RED};

use stblib::utilities::unix_time;

use tokio::io::AsyncWriteExt;
use tokio::net::TcpListener;

use crate::global::{CONFIG, LOGGER};

pub async fn connection_handler(socket: TcpListener) {
    let ignore_list: HashMap<IpAddr, u64> = HashMap::new();

    loop {
        let Ok((mut client, _)) = socket.accept().await else {
                LOGGER.error("A connection error occurred!");
                continue;
            };

        let client_addr= client.peer_addr().unwrap().ip();

        if CONFIG.networking.ratelimit && ignore_list.contains_key(&client_addr) {
            if !(unix_time() - ignore_list.get(&client_addr).unwrap()) > u64::from(CONFIG.networking.ratelimit_timeout) {
                LOGGER.info("%s (ratelimited) has connected");
                client.write_all(
                    format!("{RED}{BOLD}You have been ratelimited due to spam activity. Please try again later{C_RESET}").as_bytes()
                ).await.unwrap_or_else(|_| {
                    LOGGER.warning("warning");
                });
            }
            else {
                LOGGER.info("rlm removed");
            }
        }

        let peer = client.peer_addr().unwrap().to_string();

        client.write_all(peer.as_bytes()).await.unwrap_or_else(|_| {
           LOGGER.error("");
        });
    }
}