use std::path::Path;
use lazy_static::lazy_static;
use stblib::colors::{C_RESET, GREEN};
use stblib::stbchat::object::User;

use crate::database::mysql::MySqlDB;
use crate::database::postgresql::PostgreSqlDB;
use crate::database::sqlite::SQLiteDB;
use crate::global::{CONFIG, RUNTIME_LOGGER};
use crate::system_core::objects::{Account, UserAccount};

pub mod mysql;
pub mod postgresql;
pub mod sqlite;

#[async_trait::async_trait]
pub trait Database: Send + Sync {
    async fn hello(&self);
    async fn initialize_table(&self);
    
    async fn create_user(&self, user_id: i64, username: String, password: String, role_color: String);
    async fn delete_user(&self, username: String);

    async fn check_credentials(&self, username: &'_ str, entered_password: &'_ str) -> (UserAccount, bool);
    async fn is_username_taken(&self, username: &'_ str) -> bool;
    async fn is_account_enabled(&self, username: &'_ str) -> Option<bool>;
    async fn is_user_muted(&self, username: &'_ str) -> Option<bool>;

    async fn get_members(&self) -> Vec<String>;
    async fn get_members_by_role(&self, role: &'_ str) -> Vec<String>;
    async fn get_next_user_id(&self) -> i64;
    async fn get_user_by_name(&self, username: &'_ str) -> Option<User>;
    async fn get_account_by_name(&self, username: &'_ str) -> Option<Account>;
    async fn get_blocked_from_user(&self, username: &'_ str) -> String;
    async fn get_val_from_user(&self, username: &'_ str, value: &'_ str) -> Option<String>;

    async fn update_val(&self, username: &'_ str, key: &'_ str, value: &'_ str) -> eyre::Result<()>;
}

lazy_static!(
    pub static ref DATABASE: Box<dyn Database> = futures::executor::block_on(async {
        let url = match CONFIG.database.driver.as_str() {
            "mysql" => format!(
                "mysql://{}:{}@{}:{}/{}",
                CONFIG.database.user,
                CONFIG.database.password,
                CONFIG.database.host,
                CONFIG.database.port,
                CONFIG.database.database
            ),
            "postgresql" => format!(
                "postgresql://{}:{}@{}:{}/{}",
                CONFIG.database.user,
                CONFIG.database.password,
                CONFIG.database.host,
                CONFIG.database.port,
                CONFIG.database.database
            ),
            "sqlite" => CONFIG.database.sqlite_path.clone().unwrap().to_string(),
            _ => std::process::exit(1)
        };

        let pool: Box<dyn Database> = match CONFIG.database.driver.as_str() {
            "mysql" => Box::new(MySqlDB::new(url.as_str()).await),
            "postgres" => Box::new(PostgreSqlDB::new(url.as_str()).await),
            "sqlite" => Box::new(SQLiteDB::new(url.as_str()).await),
            _ => RUNTIME_LOGGER.panic_crash(format!("Unsupported database driver! (Supported: {GREEN}mysql, postgres, sqlite{C_RESET})")),
        };

        pool
    });
);

pub fn get_database_graph() -> (String, String) {
    let address = match CONFIG.database.driver.as_str() {
        "mysql" | "postgresql" => format!("{}:{}", CONFIG.database.host, CONFIG.database.port),
        "sqlite" => {
            let raw_path = &CONFIG.database.sqlite_path
                .clone()
                .unwrap_or_else(|| RUNTIME_LOGGER.panic_crash("You didn't provide a path for your SQLite database. Please fix your config"));

            let path = Path::new(raw_path);

            format!("sqlite://{}", path.file_name().unwrap().to_string_lossy())
        },
        _ => RUNTIME_LOGGER.panic_crash(format!("Unsupported database driver! (Supported: {GREEN}mysql, postgres, sqlite{C_RESET})")),
    };

    let graph = match CONFIG.database.driver.as_str() {
        "mysql" => format!("MySQL->{}->{}", CONFIG.database.database, CONFIG.database.table),
        "sqlite" => {
            let raw_path = &CONFIG.database.sqlite_path
                .clone()
                .unwrap_or_else(|| RUNTIME_LOGGER.panic_crash("You didn't provide a path for your SQLite database. Please fix your config"));

            let path = Path::new(raw_path);

            format!("SQLite->{}->{}", path.file_name().unwrap().to_string_lossy(), CONFIG.database.table)
        },
        "postgresql" => format!("PostgreSQL->{}->{}", CONFIG.database.database, CONFIG.database.table),
        _ => unreachable!()
    };

    (address, graph)
}