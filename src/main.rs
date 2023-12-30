#![warn(clippy::all, clippy::nursery, clippy::pedantic)]
#![allow(clippy::module_name_repetitions, clippy::should_implement_trait, clippy::struct_excessive_bools)]
#![allow(dead_code)]

use std::error::Error;

use stblib::colors::{BOLD, C_RESET, CYAN, ITALIC, MAGENTA, RESET};

use tokio::net::TcpListener;
use tokio::spawn;
use crate::communication::connection_handler::connection_handler;

use crate::global::{
    CHAT_NAME, CODENAME, CONFIG, DEFAULT_VERSION,
    RUNTIME_LOGGER, SERVER_EDITION
};
use crate::utilities::runtime_all_addresses;

mod config;
mod utilities;
mod global;
mod cli_wins;
mod communication;
mod core;

#[tokio::main]
async fn main() -> Result<(), Box<dyn Error>> {
    println!("{CYAN}{BOLD}* -- {CHAT_NAME} {} {CODENAME} ({SERVER_EDITION}) -- *{RESET}{C_RESET}", DEFAULT_VERSION.clone());

    let socket = TcpListener::bind((CONFIG.server.address.clone(), CONFIG.server.port)).await.unwrap_or_else(|err| {
        RUNTIME_LOGGER.panic(format!("{err}"));
        unreachable!()
    });

    cli_wins::feature::display();

    if !CONFIG.flags.online_mode {
        cli_wins::online_mode::display();
    }

    RUNTIME_LOGGER.info(
        format!(
            "Server is running on {ITALIC}{MAGENTA}{}:{}{C_RESET}{}",
            CONFIG.server.address, CONFIG.server.port, runtime_all_addresses()
        )
    );

    let connection_thread = spawn(connection_handler(socket));
    connection_thread.await?;

    Ok(())
}
