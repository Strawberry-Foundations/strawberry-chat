use serde::Deserialize;
use serde_yaml::{from_str, Value};

#[derive(Debug, Deserialize)]
pub struct GlobalConfig {
    pub server: ServerConfig,
    pub config: Config,
    pub network: NetworkConfig,
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
    pub max_message_length: u16,
    pub max_users: u8,
    pub max_registered_users: u8,
    pub max_username_length: u8,
    pub max_password_length: u8,
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
    pub fn new() -> Self {
        Self
    }
}