use std::collections::HashMap;
use std::net::IpAddr;

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
            if !(unix_time() - ignore_list[&client_addr]) > u64::from(CONFIG.networking.ratelimit_timeout) {
                LOGGER.info("%s (ratelimited) has connected");
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