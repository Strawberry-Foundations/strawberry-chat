use sqlx::Pool;
use sqlx::postgres::{Postgres};

use libstrawberry::stbchat::object::User;

use crate::system_core::log::log_parser;
use crate::system_core::objects::{Account, UserAccount};
use crate::constants::log_messages::DATABASE_CONNECTION_ERROR;
use crate::database::Database;
use crate::global::RUNTIME_LOGGER;

pub struct PostgreSqlDB {
    pub connection: Pool<Postgres>
}

/// # PostgreSqlDB implementation
/// WARNING: Not finished
#[allow(unused_variables)]
#[async_trait::async_trait]
impl Database for PostgreSqlDB {
    async fn hello(&self) {
        let _ = &self.connection;

        RUNTIME_LOGGER.panic_crash("PostgreSQL is currently not supported");
    }

    async fn initialize_table(&self) {
        todo!()
    }

    async fn create_user(&self, user_id: i64, username: String, password: String, role_color: String) {
        todo!()
    }

    async fn delete_user(&self, username: String) {
        todo!()
    }

    async fn check_credentials(&self, username: &'_ str, entered_password: &'_ str) -> Option<UserAccount> {
        todo!()
    }

    async fn is_username_taken(&self, username: &'_ str) -> bool {
        todo!()
    }

    async fn is_account_enabled(&self, username: &'_ str) -> Option<bool> {
        todo!()
    }

    async fn is_user_muted(&self, username: &'_ str) -> Option<bool> {
        todo!()
    }

    async fn get_members(&self) -> Vec<String> {
        todo!()
    }

    async fn get_members_by_role(&self, role: &'_ str) -> Vec<String> {
        todo!()
    }

    async fn get_next_user_id(&self) -> i64 {
        todo!()
    }

    async fn get_user_by_name(&self, username: &'_ str) -> Option<User> {
        todo!()
    }

    async fn get_account_by_name(&self, username: &'_ str) -> Option<Account> {
        todo!()
    }

    async fn get_blocked_from_user(&self, username: &'_ str) -> String {
        todo!()
    }

    async fn get_val_from_user(&self, username: &'_ str, value: &'_ str) -> Option<String> {
        todo!()
    }

    async fn update_val(&self, username: &'_ str, key: &'_ str, value: &'_ str) -> eyre::Result<()> {
        todo!()
    }
}

impl PostgreSqlDB {
    pub async fn new(url: &str) -> Self {
        let connection = Pool::<Postgres>::connect(url).await.unwrap_or_else(|err| {
            RUNTIME_LOGGER.panic_crash(log_parser(DATABASE_CONNECTION_ERROR, &[&err]));
        });

        Self {
            connection
        }
    }
}