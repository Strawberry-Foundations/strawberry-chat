use lazy_static::lazy_static;
use sqlx::{MySql, Pool};

use crate::database::mysql::Database;
use crate::global::CONFIG;

pub mod mysql;

lazy_static!(
    pub static ref DATABASE: Database = futures::executor::block_on(async {
        let url = format!(
            "mysql://{}:{}@{}:{}/{}",
            CONFIG.database.user,
            CONFIG.database.password,
            CONFIG.database.host,
            CONFIG.database.port,
            CONFIG.database.database
        );

        Database::new(url.as_str()).await
    });

    pub static ref CONNECTION: Pool<MySql> = DATABASE.connection.clone();
);