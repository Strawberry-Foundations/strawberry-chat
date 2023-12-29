#![warn(clippy::all, clippy::nursery, clippy::pedantic)]

extern crate core;

use log::{error, info};
use sqlx::ConnectOptions;
use tokio::net::TcpListener;
use tokio::spawn;
use tokio::sync::mpsc::unbounded_channel;

use crate::config::CONFIG;
use crate::connection::Connection;
use crate::message::{MessageFromClient, MessageToClient};
use crate::server_core::{handle_client, messages_handler};

mod config;
mod connection;
mod message;
mod server_core;

#[tokio::main]
async fn main() -> color_eyre::Result<()> {
    color_eyre::install().unwrap();
    simple_logger::init().unwrap();
    let listener = TcpListener::bind((CONFIG.bind.addr.clone(), CONFIG.bind.port)).await?;
    info!(
        "🍓 Strawberry Chat is running on {}:{}!",
        &CONFIG.bind.addr, CONFIG.bind.port
    );
    let (conns_tx, conns_rx) = unbounded_channel::<Connection>();
    spawn(messages_handler(conns_rx));
    loop {
        match listener.accept().await {
            Ok((stream, _)) => {
                let (from_client_tx, from_client_rx) = unbounded_channel::<MessageFromClient>();
                let (to_client_tx, to_client_rx) = unbounded_channel::<MessageToClient>();
                conns_tx
                    .send(Connection::new(&stream, from_client_rx, to_client_tx))
                    .expect("Failed to send connection through the channel");
                spawn(handle_client(stream, to_client_rx, from_client_tx));
            }
            Err(e) => error!("Failed to accept client: {e}"),
        }
    }
}
