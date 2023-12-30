#![warn(clippy::all, clippy::nursery, clippy::pedantic)]
#![allow(clippy::module_name_repetitions, clippy::should_implement_trait, clippy::struct_excessive_bools)]
#![allow(dead_code)]

use std::error::Error;

use stblib::colors::{BOLD, C_RESET, CYAN, RED, RESET};
use stblib::logging::formats::{LogFormat, LogFormatExt};
use stblib::logging::Logger;

use tokio::net::TcpListener;

use crate::global::{CHAT_NAME, CODENAME, CONFIG, DEFAULT_VERSION, SERVER_EDITION};

mod config;
mod utilities;
mod global;
mod cli_wins;

#[tokio::main]
async fn main() -> Result<(), Box<dyn Error>> {
    let runtime_logger = Logger::new(
        stblib::logging::featureset::FeatureSet::new(),
        LogFormat {
            info: String::new(),
            error: format!("{C_RESET}{BOLD}{RED}RUNTIME_ERROR{C_RESET} [%<message>%]"),
            default: String::new(),
            warning: String::new(),
            critical: String::new(),
            extensions: LogFormatExt {
                time_fmt: "%Y-%m-%d %H:%M".to_string(),
                levelname_lowercase: false
            },
        }
    );

    println!("{CYAN}{BOLD}* -- {CHAT_NAME} {} {CODENAME} ({SERVER_EDITION}) -- *{RESET}{C_RESET}", DEFAULT_VERSION.clone());

    let _socket = TcpListener::bind((CONFIG.server.address.clone(), CONFIG.server.port)).await.unwrap_or_else(|err| {
        runtime_logger.panic(format!("{}", err));
        unreachable!()
    });


    cli_wins::feature::display();

    if !CONFIG.flags.online_mode {
        cli_wins::online_mode::display();
    }



    Ok(())
}
