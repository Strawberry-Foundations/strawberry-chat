use sqlx::Pool;
use sqlx::postgres::{Postgres};

use stblib::stbchat::object::User;

use crate::system_core::log::log_parser;
use crate::system_core::objects::{Account, UserAccount};
use crate::constants::log_messages::SQL_CONNECTION_ERROR;
use crate::database::Database;
use crate::global::RUNTIME_LOGGER;

pub struct PostgreSqlDB {
    pub connection: Pool<Postgres>
}

#[allow(unused_variables)]
#[async_trait::async_trait]
impl Database for PostgreSqlDB {
    async fn create_user(&self, user_id: i64, username: String, password: String, role_color: String) {
        todo!()
    }

    async fn delete_user(&self, username: String) {
        todo!()
    }

    async fn check_credentials(&self, username: &'_ str, entered_password: &'_ str) -> (UserAccount, bool) {
        todo!()
    }

    async fn is_username_taken(&self, username: &'_ str) -> bool {
        todo!()
    }

    async fn get_members(&self) -> Vec<String> {
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

    async fn get_role_from_user(&self, username: &'_ str) -> Option<String> {
        todo!()
    }

    async fn get_muted_from_user(&self, username: &'_ str) -> bool {
        todo!()
    }
}

impl PostgreSqlDB {
    pub async fn new(url: &str) -> Self {
        let connection = Pool::<Postgres>::connect(url).await.unwrap_or_else(|err| {
            RUNTIME_LOGGER.panic_crash(log_parser(SQL_CONNECTION_ERROR, &[&err]));
        });

        Self {
            connection
        }
    }
}