pub mod db;

use sqlx::{MySql, MySqlPool, Pool};
use crate::constants::log_messages::SQL_CONNECTION_ERROR;
use crate::global::{RUNTIME_LOGGER};
use crate::system_core::log::log_parser;

pub struct Database {
    pub connection: Pool<MySql>
}

impl Database {
    pub async fn new(url: &str) -> Self {
        let connection = MySqlPool::connect(url).await.unwrap_or_else(|err| {
            RUNTIME_LOGGER.panic(log_parser(SQL_CONNECTION_ERROR, &[&err]));
            unreachable!()
        });

        Self {
            connection
        }
    }
}