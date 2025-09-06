use std::path::Path;
use lazy_static::lazy_static;
use libstrawberry::colors::{C_RESET, GREEN};
use libstrawberry::stbchat::object::User;

use crate::database::mysql::MySqlDB;
use crate::database::postgresql::PostgreSqlDB;
use crate::database::sqlite::SQLiteDB;
use crate::global::{CONFIG, RUNTIME_LOGGER};
use crate::system_core::objects::{Account, UserAccount};

pub mod mysql;
pub mod postgresql;
pub mod sqlite;

/// # Database trait
/// General functions for all compatible database systems
#[async_trait::async_trait]
pub trait Database: Send + Sync {
    /// # `hello()`
    /// Checks if the given table exists and executes a small query to ensure everything is up and working correctly
    async fn hello(&self);

    /// # `initialize_table()`
    /// Create a new table of no exists
    async fn initialize_table(&self);


    /// # `create_user()`
    /// Creates a new user
    async fn create_user(&self, user_id: i64, username: String, password: String, role_color: String);

    /// # `delete_user()`
    /// Removes a new user
    async fn delete_user(&self, username: String);


    /// # `check_credentials()`
    /// **NOTE**: NEEDS OPTIMIZATION!
    /// Checks user's credentials, returns UserAccount struct + boolean
    async fn check_credentials(&self, username: &'_ str, entered_password: &'_ str) -> Option<UserAccount>;

    /// # `is_username_taken()`
    /// Check if username is taken, returns `true` or `false`
    async fn is_username_taken(&self, username: &'_ str) -> bool;

    /// # `is_account_enabled()`
    /// Check if account is enabled, returns `true` or `false`
    async fn is_account_enabled(&self, username: &'_ str) -> Option<bool>;

    /// # `is_user_muted()`
    /// Check if username is muted, returns `true` or `false`
    async fn is_user_muted(&self, username: &'_ str) -> Option<bool>;


    /// # `get_members()`
    /// Get all members from the database, returns `Vec`
    async fn get_members(&self) -> Vec<String>;

    /// # `get_members_by_role()`
    /// Get all members from the database WHERE specific role, returns `Vec`
    async fn get_members_by_role(&self, role: &'_ str) -> Vec<String>;

    /// # `get_next_user_id()`
    /// Get the next available user id, returns `int`
    async fn get_next_user_id(&self) -> i64;

    /// # `get_user_by_name()`
    /// Get user by their name, returns `User`
    async fn get_user_by_name(&self, username: &'_ str) -> Option<User>;

    /// # `get_account_by_name()`
    /// Get user's full account by their name, returns `User`
    async fn get_account_by_name(&self, username: &'_ str) -> Option<Account>;

    /// # `get_blocked_from_user()`
    /// Get user's blocked accounts, returns `String`
    async fn get_blocked_from_user(&self, username: &'_ str) -> String;

    /// # `get_val_from_user()`
    /// Get a value from user, returns `Option<String>`
    async fn get_val_from_user(&self, username: &'_ str, value: &'_ str) -> Option<String>;


    /// # `update_val()`
    /// Update a value, returns `Result`
    async fn update_val(&self, username: &'_ str, key: &'_ str, value: &'_ str) -> eyre::Result<()>;
}

lazy_static!(
    pub static ref DATABASE: Box<dyn Database> = futures::executor::block_on(async {
        /// get_database_graph() is executed before this so no proper error handling is needed here
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

        /// Create database pool
        let pool: Box<dyn Database> = match CONFIG.database.driver.as_str() {
            "mysql" => Box::new(MySqlDB::new(url.as_str()).await),
            "postgresql" => Box::new(PostgreSqlDB::new(url.as_str()).await),
            "sqlite" => Box::new(SQLiteDB::new(url.as_str()).await),
            _ => RUNTIME_LOGGER.panic_crash(format!("Unsupported database driver! (Supported: {GREEN}mysql, postgres, sqlite{C_RESET})")),
        };

        pool
    });
);

/// # `get_database_graph()`
/// Create a small visual database graph for startup of strawberry chat
/// Handles errors e.g. unsupported database driver, missing `SQLite` path, ...
pub fn get_database_graph() -> (String, String) {
    /// Create address graph (e.g. `example.org:3306`, `sqlite://users.db`)
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

    /// Create database graph (e.g. `MySQL->data->users`, `SQLite->users.db->users`
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