#![warn(clippy::all, clippy::nursery, clippy::pedantic)]
#![allow(clippy::module_name_repetitions, clippy::should_implement_trait, clippy::struct_excessive_bools)]
#![allow(dead_code)]

use std::error::Error;
use stblib::colors::{BLUE, BOLD, C_RESET, CYAN, RED, RESET, YELLOW};
use stblib::logging::formats::{LogFormat, LogFormatExt};
use stblib::logging::Logger;
use tokio::net::TcpListener;
use crate::global::{CHAT_NAME, CODENAME, CONFIG, DEFAULT_VERSION, LOGGER, SERVER_EDITION};

mod config;
mod utilities;
mod global;

#[tokio::main]
async fn main() -> Result<(), Box<dyn Error>> {
    let runtime_logger = Logger::new(
        stblib::logging::featureset::FeatureSet::new(),
        LogFormat {
            info: "".to_string(),
            error: format!("{C_RESET}{BOLD}{RED}RUNTIME_ERROR{C_RESET} [%<message>%]"),
            default: "".to_string(),
            warning: "".to_string(),
            critical: "".to_string(),
            extensions: LogFormatExt {
                time_fmt: "%Y-%m-%d %H:%M".to_string(),
                levelname_lowercase: false
            },
        }
    );

    println!("{CYAN}{BOLD}* -- {CHAT_NAME} {} {CODENAME} ({SERVER_EDITION}) -- *{RESET}{C_RESET}", DEFAULT_VERSION.clone());

    let socket = TcpListener::bind((CONFIG.server.address.clone(), CONFIG.server.port)).await.unwrap_or_else(|err| {
        runtime_logger.panic(format!("{}", err).as_str());
        unreachable!()
    });



    Ok(())
}
