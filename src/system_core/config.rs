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
    pub config_ver: String,

    #[serde(skip)]
    pub path: String,
}

#[derive(Debug, Deserialize)]
pub struct ServerConfig {
    pub address: String,
    pub port: u16,
    pub name: String,
    pub title: String,
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
    pub watchdog_timeout: u64,
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

pub const DEFAULT_CONFIG: &str = r#"server:
  address: "0.0.0.0"
  port: 52800
  name: "Strawberry Chat Server"
  title: "Julian's Strawberry Chat"
  description: "This is Julian's Strawberry Chat instance!"
  edition_key: "somekey"
  update_channel: "stable"

config:
  max_message_length: 256
  max_users: -1
  max_registered_users: -1
  max_username_length: 32
  max_password_length: 256
  recv_allowed_bytes: 8192
  watchdog_timeout: 4

networking:
  ratelimit: true
  ratelimit_timeout: 30

flags:
  enable_messages: true
  enable_queue: true
  debug_mode: false
  online_mode: true
  admins_wait_queue: false
  bots_wait_queue: true
  special_messages: false

database:
  driver: mysql       # Available drivers: mysql

  host: localhost
  port: 3006
  user: admin
  password: admin
  database_name: data
  database_table: users

security:
  require_signing: false
  signing_key: none
  banned_ips: []


config_ver: 9"#;

impl GlobalConfig {
    pub fn new(config_path: String) -> Self {
        let cfg_content = utilities::open_config(&config_path);

        let mut config: Self = from_str(&cfg_content).unwrap_or_else(|err| {
            LOGGER.critical_panic(format!("Could not read configuration: {err}"));
        });

        config.path = config_path;

        config
    }
}