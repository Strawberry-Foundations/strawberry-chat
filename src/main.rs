#![warn(clippy::all, clippy::nursery, clippy::pedantic)]
#![allow(
    clippy::module_name_repetitions, clippy::struct_excessive_bools, clippy::missing_const_for_fn, clippy::const_is_empty,
    dead_code, unused_doc_comments,
)]

use std::env::var;
use std::sync::{Mutex, OnceLock};

use tokio::spawn;
use tokio::sync::mpsc::channel;
use tokio::net::TcpListener;
use tokio::task::JoinHandle;

use libstrawberry::colors::{YELLOW, CYAN, MAGENTA, BOLD, C_RESET, ITALIC, RESET};
use crate::system_core::server_core::core_thread;
use crate::system_core::watchdog::watchdog_thread;
use crate::system_core::panic::panic_handler;
use crate::communication::connection_handler::connection_handler;
use crate::utilities::runtime_all_addresses;
use crate::database::{get_database_graph, DATABASE};
use crate::global::{CONFIG, DEFAULT_VERSION, ONLINE_MODE, RUNTIME_LOGGER, CHAT_NAME, CODENAME, SERVER_EDITION, ADDITION_VER};
use crate::cli_wins::constructor::{Constructor, ConstructorOptions};

mod utilities;
mod global;
mod cli_wins;
mod communication;
mod system_core;
mod constants;
mod commands;
mod database;
mod security;

pub static CORE_HANDLE: OnceLock<Mutex<JoinHandle<()>>> = OnceLock::new();


#[tokio::main]
async fn main(){
    std::panic::set_hook(Box::new(|info| {
        panic_handler(info);
    }));

    println!("{CYAN}{BOLD}* -- {CHAT_NAME} {} {CODENAME} ({SERVER_EDITION}) -- *{RESET}{C_RESET}", DEFAULT_VERSION.clone());
    
    if !ADDITION_VER.is_empty() {
        let constructor = Constructor::new("Pre-released Software", YELLOW, 2, ConstructorOptions {
            debug_mode: true
        });

        let window = constructor.builder()
            .label("Some features are still missing", format!("{BOLD}{YELLOW}"))
            .build();

        window.show();
    }

    if var("DEBUG").is_ok() {
        println!();

        let constructor = Constructor::new("Warning: Debug Mode", YELLOW, 2, ConstructorOptions {
            debug_mode: true
        });

        let window = constructor.builder()
            .label("Strawberry Chat is running in Debug Mode", format!("{BOLD}{YELLOW}"))
            .build();

        window.show();
    }

    let socket = TcpListener::bind((CONFIG.server.address.clone(), CONFIG.server.port)).await.unwrap_or_else(|err| {
        RUNTIME_LOGGER.panic_crash(format!("{err}"));
    });

    cli_wins::feature::display();

    if !CONFIG.flags.online_mode {
        cli_wins::online_mode::display();
    }

    ONLINE_MODE.auth().await;

    let (db_address, db_graph) = get_database_graph();

    RUNTIME_LOGGER.default(format!("Connecting to database on address {ITALIC}{CYAN}{db_address}{RESET} ..."));
    DATABASE.hello().await;
    RUNTIME_LOGGER.default(format!("Connected to {ITALIC}{CYAN}{db_address}{RESET} ({db_graph})"));


    RUNTIME_LOGGER.info(
        format!(
            "Server is running on {ITALIC}{MAGENTA}{}:{}{C_RESET}{}",
            CONFIG.server.address, CONFIG.server.port, runtime_all_addresses()
        )
    );

    let (wd_tx, wd_rx) = channel::<()>(1);

    spawn(connection_handler(socket));
    spawn(watchdog_thread(wd_rx));

    CORE_HANDLE.set(Mutex::new(spawn(core_thread(wd_tx)))).unwrap();

    std::thread::park();
}
