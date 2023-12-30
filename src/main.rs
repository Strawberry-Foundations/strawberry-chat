#![warn(clippy::all, clippy::nursery, clippy::pedantic)]
#![allow(clippy::module_name_repetitions, clippy::should_implement_trait, clippy::struct_excessive_bools)]
#![allow(dead_code)]

use std::error::Error;
use stblib::colors::{BOLD, C_RESET, CYAN, RESET};
use tokio::net::TcpListener;
use crate::global::{CHAT_NAME, CODENAME, CONFIG, DEFAULT_VERSION, EXT_VERSION, SERVER_EDITION};

mod config;
mod utilities;
mod global;

#[tokio::main]
async fn main() -> Result<(), Box<dyn Error>> {
    println!("{CYAN}{BOLD}* -- {CHAT_NAME} {} {CODENAME} ({SERVER_EDITION}) -- *{RESET}{C_RESET}", DEFAULT_VERSION.clone());
    println!("{}", EXT_VERSION.clone());
    let socket = TcpListener::bind((CONFIG.server.address.clone(), CONFIG.server.port)).await?;
    Ok(())
}
