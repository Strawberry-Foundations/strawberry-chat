#![warn(clippy::all, clippy::nursery, clippy::pedantic)]
#![allow(clippy::module_name_repetitions, clippy::should_implement_trait, clippy::struct_excessive_bools)]
#![allow(dead_code)]

use std::error::Error;
use stblib::colors::{BOLD, C_RESET, CYAN, RED, RESET, WHITE, YELLOW};
use stblib::logging::formats::{LogFormat, LogFormatExt};
use stblib::logging::Logger;
use tokio::net::TcpListener;
use crate::global::{CHAT_NAME, CODENAME, CONFIG, DEFAULT_VERSION, SERVER_EDITION};
use crate::utilities::{get_ratelimit_timeout, is_feature_enabled};

mod config;
mod utilities;
mod global;

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

    println!("\n{BOLD}  {CYAN}* -------------- FEATURES -------------- *{RESET}{C_RESET}");
    println!("{BOLD}  {CYAN}|{WHITE} *{YELLOW} Console Message Logging is {}{CYAN}  |{RESET}{C_RESET}",
             is_feature_enabled(CONFIG.flags.enable_messages)
    );
    println!("{BOLD}  {CYAN}|{WHITE} *{YELLOW} Debug Mode is {}             {CYAN}  |{RESET}{C_RESET}",
             is_feature_enabled(CONFIG.flags.debug_mode)
    );
    println!("{BOLD}  {CYAN}|{WHITE} *{YELLOW} Ratelimit is {}{}        {CYAN}|{RESET}{C_RESET}",
             is_feature_enabled(CONFIG.networking.ratelimit), get_ratelimit_timeout(CONFIG.networking.ratelimit)
    );
    println!("{BOLD}  {CYAN}* -------------------------------------- *{RESET}{C_RESET}\n");



    Ok(())
}
