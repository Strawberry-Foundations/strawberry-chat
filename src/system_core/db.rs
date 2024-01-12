use futures::executor::block_on;
use lazy_static::lazy_static;
use sha2::{Digest, Sha512};
use sqlx::mysql::MySqlPool;
use sqlx::{Executor, FromRow, Pool, MySql};
use crate::global::CONFIG;

fn sha512_hash(text: String) -> String {
    let hash = Sha512::digest(text.as_bytes());
    hex::encode(hash)
}

#[derive(FromRow)]
pub struct DatabaseRecord {
    name: String,
    nick: Option<String>,
    /// 0: Normal
    /// 1: Moderator
    /// 2: Admin
    /// 3: Owner
    permission_level: i32,
    /// SHA-512 hashed password
    password: String,
}

lazy_static! {
    pub static ref DATABASE: Pool<MySql> = block_on(async {
        let db_url = format!(
            "mysql://{}:{}@{}/{}",
            CONFIG.database.user, CONFIG.database.password, CONFIG.database.host, CONFIG.database.database_name
        );

        let db = MySqlPool::connect(db_url.as_str()).await.expect("Failed to connect to database");

        db.execute("CREATE TABLE users (
        user_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
        username TEXT NOT NULL, password TEXT NOT NULL,
        nickname TEXT DEFAULT '',
        description TEXT DEFAULT '',
        badge TEXT DEFAULT '',
        badges TEXT DEFAULT '',
        avatar_url TEXT NOT NULL DEFAULT '',
        role TEXT NOT NULL,
        role_color TEXT NOT NULL,
        enable_blacklisted_words TEXT NOT NULL,
        account_enabled TEXT NOT NULL,
        enable_dms TEXT NOT NULL,
        muted TEXT NOT NULL,
        strawberry_id TEXT DEFAULT '',
        discord_name TEXT DEFAULT '',
        msg_count INT NOT NULL,
        creation_date INT NOT NULL,
	    blocked_users TEXT DEFAULT '');").await.expect("Failed to execute query");

        db
    });
}

pub async fn add_user(name: String, password: String) -> Result</* User created? */ bool, sqlx::Error> {
    if sqlx::query("SELECT * FROM users WHERE username=$1")
        .bind(&name)
        .fetch_optional(&DATABASE.clone())
        .await
        .expect("Failed to execute query")
        .is_some()
    {
        return Ok(false);
    };
    sqlx::query("INSERT INTO users (username, role, password) VALUES ($1, 0, $2)")
        .bind(&name)
        .bind(sha512_hash(password))
        .execute(&DATABASE.clone())
        .await?;
    Ok(true)
}

pub async fn check_login(name: String, password: String) -> Result<bool, sqlx::Error> {
    let Some(user) =
        sqlx::query_as::<_, DatabaseRecord>("SELECT * FROM users WHERE username=$1")
            .bind(&name)
            .fetch_optional(&DATABASE.clone())
            .await?
    else {
        return Ok(false);
    };

    return Ok(user.password == sha512_hash(password));
}
