use lazy_static::lazy_static;
use sqlx::sqlite::SqliteConnectOptions;
use sqlx::{Pool, Sqlite, SqlitePool};

lazy_static! {
    pub static ref POOL: Pool<Sqlite> = futures::executor::block_on(async {
        let opts = SqliteConnectOptions::new()
            .filename("stbchat.db")
            .create_if_missing(true);
        SqlitePool::connect_with(opts)
            .await
            .expect("Database error")
    });
}
