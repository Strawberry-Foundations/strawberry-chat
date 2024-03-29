#![warn(clippy::all, clippy::nursery, clippy::pedantic)]
#![allow(clippy::module_name_repetitions, clippy::struct_excessive_bools, dead_code, unused_doc_comments, clippy::missing_const_for_fn)]

use std::env::var;
use std::sync::{Mutex, OnceLock};

use tokio::spawn;
use tokio::net::TcpListener;
use tokio::sync::mpsc::channel;
use tokio::task::JoinHandle;

use stblib::colors::{BOLD, C_RESET, CYAN, ITALIC, MAGENTA, RESET, YELLOW};

use crate::communication::connection_handler::connection_handler;
use crate::database::db::DATABASE;
use crate::global::{CHAT_NAME, CODENAME, CONFIG, DEFAULT_VERSION, ONLINE_MODE, RUNTIME_LOGGER, SERVER_EDITION};
use crate::system_core::server_core::core_thread;
use crate::system_core::watchdog::watchdog_thread;
use crate::utilities::{delete_last_line, runtime_all_addresses};

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
    println!("{CYAN}{BOLD}* -- {CHAT_NAME} {} {CODENAME} ({SERVER_EDITION}) -- *{RESET}{C_RESET}", DEFAULT_VERSION.clone());

    let constructor = cli_wins::constructor::Constructor::new("Beta Software", YELLOW, 2, cli_wins::constructor::ConstructorOptions {
        debug_mode: true
    });

    let window = constructor.builder()
        .label("Some features are still missing", format!("{BOLD}{YELLOW}"))
        .build();

    window.show();

    if var("DEBUG").is_ok() {
        println!();

        let constructor = cli_wins::constructor::Constructor::new("Warning: Debug Mode", YELLOW, 2, cli_wins::constructor::ConstructorOptions {
            debug_mode: true
        });

        let window = constructor.builder()
            .label("Strawberry Chat is running in Debug Mode", format!("{BOLD}{YELLOW}"))
            .build();

        window.show();
    }

    let socket = TcpListener::bind((CONFIG.server.address.clone(), CONFIG.server.port)).await.unwrap_or_else(|err| {
        RUNTIME_LOGGER.panic(format!("{err}"));
    });

    cli_wins::feature::display();

    if !CONFIG.flags.online_mode {
        cli_wins::online_mode::display();
    }

    ONLINE_MODE.auth().await;

    RUNTIME_LOGGER.default(format!("Connecting to database on address {}", CONFIG.database.host));
    let _ = DATABASE.connection.clone();

    delete_last_line();
    RUNTIME_LOGGER.default(format!("Connected to {}", CONFIG.database.host));


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
