#![warn(clippy::all, clippy::nursery, clippy::pedantic)]
#![allow(clippy::module_name_repetitions, clippy::should_implement_trait, clippy::struct_excessive_bools, dead_code, unused_doc_comments, clippy::missing_const_for_fn)]

use std::error::Error;

use tokio::net::TcpListener;

use stblib::colors::{BOLD, C_RESET, CYAN, ITALIC, MAGENTA, RESET};
use tokio::spawn;

use crate::communication::connection_handler::connection_handler;
use crate::global::{CHAT_NAME, CODENAME, CONFIG, DEFAULT_VERSION, RUNTIME_LOGGER, SERVER_EDITION};
use crate::system_core::server_core::core_thread;
use crate::utilities::runtime_all_addresses;

mod utilities;
mod global;
mod cli_wins;
mod communication;
mod system_core;
mod constants;

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

    spawn(core_thread());
    connection_handler(socket).await;

    Ok(())
}
