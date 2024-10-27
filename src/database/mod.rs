use lazy_static::lazy_static;
use sqlx::{MySql, Pool};
use sqlx::mysql::MySqlRow;
use stblib::stbchat::object::User;

use crate::database::mysql::{MySqlDB, MySqlOld};
use crate::database::postgresql::PostgreSqlDB;
use crate::global::CONFIG;
use crate::system_core::objects::{Account, UserAccount};

pub mod mysql;
mod postgresql;

#[async_trait::async_trait]
pub trait Database: Send + Sync {
    async fn create_user(&self, user_id: i64, username: String, password: String, role_color: String);
    async fn delete_user(&self, username: String);
    async fn fetch_members(&self) -> Vec<MySqlRow>;
    async fn check_credentials(&self, username: &'_ str, entered_password: &'_ str) -> (UserAccount, bool);
    async fn is_username_taken(&self, username: &'_ str) -> bool;
    async fn get_next_user_id(&self) -> i64;
    async fn get_user_by_name(&self, username: &'_ str) -> Option<User>;
    async fn get_account_by_name(&self, username: &'_ str) -> Option<Account>;
}

lazy_static!(
    pub static ref DATABASE: MySqlOld = futures::executor::block_on(async {
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
            _ => std::process::exit(1)
        };

        MySqlOld::new(url.as_str()).await
    });

    pub static ref CONNECTION: Pool<MySql> = DATABASE.connection.clone();
);