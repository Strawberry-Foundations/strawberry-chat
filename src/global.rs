use std::env;
use std::path::{Path, PathBuf};
use std::sync::LazyLock;

use libstrawberry::colors::{BLUE, BOLD, C_RESET, CYAN, GREEN, RED, YELLOW};
use libstrawberry::logging::Logger;
use libstrawberry::logging::formats::{LogFormat, LogFormatOptions};

use crate::security::online_mode::OnlineMode;
use crate::security::verification::MessageVerification;
use crate::system_core::config::GlobalConfig;

pub const STRAWBERRY_API: &str = "https://api.strawberryfoundations.org/v2/";
pub const STRAWBERRY_ID_API: &str = "https://id.strawberryfoundations.org/v2/";
pub const STRAWBERRY_CLOUD_API: &str = "https://cloud.strawberryfoundations.org/";

pub const BASE_VERSION: &str = "1.13.2";
pub const CORE_BASE_VERSION: &str = "1.05";
pub const ADDITION_VER: &str = "";
pub const STBM_VER: &str = "3";
pub const CONFIG_VER: &str = "10";

pub const CODENAME: &str = "Rusty Cake";
pub const CODENAME_SHORT: &str = "rscake";

pub const CHAT_NAME: &str = "Strawberry Chat";
pub const UPDATE_CHANNEL: &str = "stable";
pub const SERVER_EDITION: &str = "Community";

pub const AUTHORS: &[&str; 3] = &["Juliandev02", "Paddyk45", "matteodev8"];

pub static LOGGER: LazyLock<Logger> = LazyLock::new(|| {
    Logger::new(
        libstrawberry::logging::features::LoggingFeatures::new(),
        libstrawberry::logging::formats::default_fmt(),
    )
});

pub static RUNTIME_LOGGER: LazyLock<Logger> = LazyLock::new(|| {
    Logger::new(
        libstrawberry::logging::features::LoggingFeatures::new(),
        LogFormat {
            info: format!("{C_RESET}{BOLD}{GREEN}STARTUP{C_RESET}  [%<message>%]"),
            error: format!("{C_RESET}{BOLD}{RED}ERR{C_RESET}      [%<message>%]"),
            ok: format!("{C_RESET}{BOLD}{BLUE}DATABASE{C_RESET} [%<message>%]"),
            warning: format!("{C_RESET}{BOLD}{YELLOW}WARNING{C_RESET}  [%<message>%]"),
            panic: format!("{C_RESET}{BOLD}{RED}PANIC{C_RESET}    [%<message>%]"),
            critical: String::new(),
            log_options: LogFormatOptions {
                timestamp_format: "%Y-%m-%d %H:%M".to_string(),
                levelname_lowercase: false,
            },
        },
    )
});

pub static CONFIG: LazyLock<GlobalConfig> = LazyLock::new(|| {
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

    let config = GlobalConfig::new(config_path);

    if CONFIG_VER != config.config_ver {
        RUNTIME_LOGGER.panic(format!(
            "Config version is invalid - Please update your config. \
                    (currently: {YELLOW}{}{C_RESET}, requires: {CYAN}{CONFIG_VER}{C_RESET})",
            config.config_ver
        ));
    }

    config
});

pub static DEFAULT_VERSION: LazyLock<String> = LazyLock::new(|| format!("v{BASE_VERSION}{ADDITION_VER}"));
pub static VERSION: LazyLock<String> = LazyLock::new(|| DEFAULT_VERSION.clone());
pub static CORE_VERSION: LazyLock<String> = LazyLock::new(|| format!("{BASE_VERSION}-{CODENAME_SHORT}-{CORE_BASE_VERSION}"));
pub static EXT_VERSION: LazyLock<String> = LazyLock::new(|| {
    format!(
        "{}_{}-{CODENAME_SHORT}-rst_stbcv{STBM_VER}",
        DEFAULT_VERSION.clone(),
        UPDATE_CHANNEL
    )
});
pub static MESSAGE_VERIFICATOR: LazyLock<MessageVerification> = LazyLock::new(MessageVerification::new);
pub static ONLINE_MODE: LazyLock<OnlineMode> = LazyLock::new(|| OnlineMode::new(CONFIG.flags.online_mode));
