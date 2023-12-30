use std::collections::HashMap;
use std::net::Ipv4Addr;
use tokio::io::AsyncWriteExt;
use tokio::net::TcpListener;
use crate::global::{CONFIG, LOGGER};

pub async fn connection_handler(socket: TcpListener) {
    let ignore_list: HashMap<Ipv4Addr, u32> = HashMap::new();

    loop {
        let (mut client, _) = match socket.accept().await {
            Ok((client, addr)) => (client, addr),
            Err(_) => {
                LOGGER.error("A connection error occured!");
                continue;
            }
        };

        if CONFIG.networking.ratelimit {
            if ignore_list.contains_key(client.peer_addr().unwrap()) {

            }
        }

        let peer = client.peer_addr().unwrap().to_string();

        client.write_all(peer.as_bytes()).await.unwrap_or_else(|_| {
           LOGGER.error("");
        });
    }
}