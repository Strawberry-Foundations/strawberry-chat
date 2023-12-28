#![warn(clippy::all, clippy::nursery, clippy::pedantic)]

extern crate core;

use log::{error, info};
use tokio::net::{TcpListener, TcpStream};
use tokio::spawn;
use tokio::sync::mpsc::{unbounded_channel, UnboundedReceiver, UnboundedSender};

use crate::config::CONFIG;
use crate::connection::Connection;
use crate::message::{MessageFromClient, MessageToClient};

mod config;
mod connection;
mod message;

async fn handle_client(
    stream: TcpStream,
    rx: UnboundedReceiver<MessageToClient>,
    tx: UnboundedSender<MessageFromClient>,
) {
    todo!();
}

#[tokio::main]
async fn main() -> color_eyre::Result<()> {
    let listener = TcpListener::bind((CONFIG.bind.addr.clone(), CONFIG.bind.port)).await?;
    info!(
        "🍓 Strawberry Chat is running on {}:{}!",
        &CONFIG.bind.addr, CONFIG.bind.port
    );
    let mut clients = vec![];
    loop {
        match listener.accept().await {
            Ok((stream, _)) => {
                let (from_client_tx, from_client_rx) = unbounded_channel::<MessageFromClient>();
                let (to_client_tx, to_client_rx) = unbounded_channel::<MessageToClient>();
                clients.push(Connection::new(&stream, from_client_rx, to_client_tx));
                spawn(handle_client(stream, to_client_rx, from_client_tx));
            }
            Err(e) => error!("Failed to accept client: {e}"),
        }
    }
}
