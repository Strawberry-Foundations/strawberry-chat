use lazy_static::lazy_static;
use sqlx::mysql::MySqlRow;
use stblib::stbchat::object::User;

use crate::database::mysql::MySqlDB;
use crate::database::postgresql::PostgreSqlDB;
use crate::database::sqlite::SQLiteDB;
use crate::global::CONFIG;
use crate::system_core::objects::{Account, UserAccount};

pub mod mysql;
pub mod postgresql;
pub mod sqlite;

#[async_trait::async_trait]
pub trait Database: Send + Sync {
    async fn create_user(&self, user_id: i64, username: String, password: String, role_color: String);
    async fn delete_user(&self, username: String);

    async fn check_credentials(&self, username: &'_ str, entered_password: &'_ str) -> (UserAccount, bool);
    async fn is_username_taken(&self, username: &'_ str) -> bool;

    async fn get_members(&self) -> Vec<MySqlRow>;
    async fn get_next_user_id(&self) -> i64;
    async fn get_user_by_name(&self, username: &'_ str) -> Option<User>;
    async fn get_account_by_name(&self, username: &'_ str) -> Option<Account>;
    async fn get_blocked_from_user(&self, username: &'_ str) -> String;
    async fn get_role_from_user(&self, username: &'_ str) -> Option<String>;
    async fn get_muted_from_user(&self, username: &'_ str) -> bool;
}

lazy_static!(
    pub static ref DATABASE: Box<dyn Database> = futures::executor::block_on(async {
        let url = format!(
            "mysql://{}:{}@{}:{}/{}",
            CONFIG.database.user,
            CONFIG.database.password,
            CONFIG.database.host,
            CONFIG.database.port,
            CONFIG.database.database
        );

        let pool: Box<dyn Database> = match CONFIG.database.driver.as_str() {
            "mysql" => Box::new(MySqlDB::new(url.as_str()).await),
            "postgres" => Box::new(PostgreSqlDB::new(url.as_str()).await),
            "sqlite" => Box::new(SQLiteDB::new(url.as_str()).await),
            _ => std::process::exit(1)
        };

        pool
    });
);