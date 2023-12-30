#![warn(clippy::all, clippy::nursery, clippy::pedantic)]
#![allow(clippy::module_name_repetitions, clippy::should_implement_trait, clippy::struct_excessive_bools)]
#![allow(dead_code)]

use std::error::Error;

use stblib::colors::{BOLD, C_RESET, CYAN, RESET};

use tokio::net::TcpListener;

use crate::global::{
    CHAT_NAME, CODENAME, CONFIG, DEFAULT_VERSION,
    RUNTIME_LOGGER, SERVER_EDITION
};

mod config;
mod utilities;
mod global;
mod cli_wins;

#[tokio::main]
async fn main() -> Result<(), Box<dyn Error>> {
    println!("{CYAN}{BOLD}* -- {CHAT_NAME} {} {CODENAME} ({SERVER_EDITION}) -- *{RESET}{C_RESET}", DEFAULT_VERSION.clone());

    let _socket = TcpListener::bind((CONFIG.server.address.clone(), CONFIG.server.port)).await.unwrap_or_else(|err| {
        RUNTIME_LOGGER.panic(format!("{}", err));
        unreachable!()
    });

    cli_wins::feature::display();

    if !CONFIG.flags.online_mode {
        cli_wins::online_mode::display();
    }





    Ok(())
}
