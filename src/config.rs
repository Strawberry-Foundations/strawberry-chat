use serde::Deserialize;
use serde_yaml::from_str;
use crate::global::LOGGER;

use crate::utilities;

#[derive(Debug, Deserialize)]
pub struct GlobalConfig {
    pub server: ServerConfig,
    pub config: Config,
    pub networking: NetworkConfig,
    pub flags: FlagConfig,
    pub database: DatabaseConfig,
    pub security: SecurityConfig,

    #[serde(skip)]
    pub path: String,
}

#[derive(Debug, Deserialize)]
pub struct ServerConfig {
    pub address: String,
    pub port: u16,
    pub name: String,
    pub description: String,
    pub edition_key: String,
    pub update_channel: String,
}

#[derive(Debug, Deserialize)]
pub struct Config {
    pub max_message_length: i16,
    pub max_users: i16,
    pub max_registered_users: i16,
    pub max_username_length: u16,
    pub max_password_length: u16,
    pub recv_allowed_bytes: u16,
}

#[derive(Debug, Deserialize)]
pub struct NetworkConfig {
    pub ratelimit: bool,
    pub ratelimit_timeout: u16,
}

#[derive(Debug, Deserialize)]
pub struct FlagConfig {
    pub enable_messages: bool,
    pub enable_queue: bool,
    pub debug_mode: bool,
    pub online_mode: bool,
    pub admins_wait_queue: bool,
    pub bots_wait_queue: bool,
    pub special_messages: bool,
}

#[derive(Debug, Deserialize)]
pub struct DatabaseConfig {
    pub driver: String,
    pub check_same_thread: bool,
    pub host: String,
    pub port: u16,
    pub user: String,
    pub password: String,
    pub database_name: String,
    pub database_table: String,
}

#[derive(Debug, Deserialize)]
pub struct SecurityConfig {
    pub require_signing: bool,
    pub signing_key: String,
    pub banned_ips: Vec<String>
}



impl GlobalConfig {
    pub fn new(config_path: String) -> Self {
        let cfg_content = utilities::open_config(&config_path);

        let mut config: Self = from_str(&cfg_content).unwrap_or_else(|err| {
            LOGGER.panic_critical(format!("Could not read configuration: {err}"));
            unreachable!()
        });

        config.path = config_path;

        config
    }
}