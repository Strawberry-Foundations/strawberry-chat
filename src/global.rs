use std::env;
use std::path::{Path, PathBuf};
use std::string::ToString;

use lazy_static::lazy_static;

use stblib::logging::Logger;
use stblib::colors::{BLUE, BOLD, C_RESET, GREEN, RED, YELLOW};
use stblib::logging::formats::{LogFormat, LogFormatExt};

use crate::system_core::config::GlobalConfig;
use crate::security::verification::MessageVerification;
use crate::security::online_mode::OnlineMode;

pub const API: &str = "https://api.strawberryfoundations.xyz/v1/";

pub const BASE_VERSION: &str = "1.11.0";
pub const ADDITION_VER: &str = "a6";
pub const STBM_VER: &str = "3";

pub const CODENAME: &str = "Vanilla Cake";
pub const CODENAME_SHORT: &str = "vacakes";

pub const CHAT_NAME: &str = "Strawberry Chat";
pub const UPDATE_CHANNEL: &str = "canary";
pub const SERVER_EDITION: &str = "Rusty Edition";

pub const AUTHORS: &[&str; 3] = &["Juliandev02", "Paddyk45", "matteodev8"];

lazy_static! {
    pub static ref LOGGER: Logger = Logger::new(
        stblib::logging::featureset::FeatureSet::new(),
        stblib::logging::formats::strawberry_chat_fmt()
    );

    pub static ref RUNTIME_LOGGER: Logger = Logger::new(
        stblib::logging::featureset::FeatureSet::new(),
        LogFormat {
            info: format!("{C_RESET}{BOLD}{GREEN}STARTUP{C_RESET}  [%<message>%]"),
            error: format!("{C_RESET}{BOLD}{RED}RUNTIME_ERROR{C_RESET} [%<message>%]"),
            default: format!("{C_RESET}{BOLD}{BLUE}DATABASE{C_RESET} [%<message>%]"),
            warning: format!("{C_RESET}{BOLD}{YELLOW}WARNING{C_RESET} [%<message>%]"),
            critical: String::new(),
            extensions: LogFormatExt {
                time_fmt: "%Y-%m-%d %H:%M".to_string(),
                levelname_lowercase: false
            },
        }
    );

    pub static ref CONFIG: GlobalConfig = {
        let exe_path = env::current_exe().unwrap_or_else(|_| {
            LOGGER.panic("Could not get your Strawberry Chat Runtime Executable");
        });

        let exe_dir = exe_path.parent().unwrap_or_else(|| {
            LOGGER.panic("Could not get directory of your Strawberry Chat Runtime Executable");
        });

        let exe_dir_str = PathBuf::from(exe_dir).display().to_string();

        let mut config_path = format!("{exe_dir_str}/config.yml");

        if !Path::new(&config_path).exists() {
            config_path = String::from("./config.yml");
        }

        GlobalConfig::new(config_path)
    };

    pub static ref DEFAULT_VERSION: String = format!("v{BASE_VERSION}{ADDITION_VER}");
    pub static ref VERSION: String = format!("{}", DEFAULT_VERSION.clone());

    pub static ref EXT_VERSION: String = format!(
        "{}_{UPDATE_CHANNEL}-{CODENAME_SHORT}-rst_stbcv{STBM_VER}",
        DEFAULT_VERSION.clone()
    );

    pub static ref MESSAGE_VERIFICATOR: MessageVerification = MessageVerification::new();

    pub static ref ONLINE_MODE: OnlineMode = OnlineMode::new(CONFIG.flags.online_mode);
}