use sqlx::Pool;
use sqlx::sqlite::{Sqlite};

use stblib::stbchat::object::User;

use crate::system_core::log::log_parser;
use crate::system_core::objects::{Account, UserAccount};
use crate::constants::log_messages::SQL_CONNECTION_ERROR;
use crate::database::Database;
use crate::global::RUNTIME_LOGGER;

pub struct SQLiteDB {
    pub connection: Pool<Sqlite>
}

#[allow(unused_variables)]
#[async_trait::async_trait]
impl Database for SQLiteDB {
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

    async fn get_val_from_user(&self, username: &'_ str, value: &'_ str) -> Option<String> {
        todo!()
    }

    async fn get_muted_from_user(&self, username: &'_ str) -> bool {
        todo!()
    }

    async fn update_val(&self, username: &'_ str, key: &'_ str, value: &'_ str) {
        todo!()
    }
}

impl SQLiteDB {
    pub async fn new(url: &str) -> Self {
        let connection = Pool::<Sqlite>::connect(url).await.unwrap_or_else(|err| {
            RUNTIME_LOGGER.panic_crash(log_parser(SQL_CONNECTION_ERROR, &[&err]));
        });

        Self {
            connection
        }
    }
}