use futures::executor::block_on;
use lazy_static::lazy_static;
use sha2::{Digest, Sha512};
use sqlx::postgres::PgPoolOptions;
use sqlx::{Executor, FromRow, Pool, Postgres};

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
    static ref DATABASE: Pool<Postgres> = block_on(async {
        let db_url = env!("DB_URL");
        let db = PgPoolOptions::new()
            .connect(db_url)
            .await
            .expect("Failed to connect to database");
        db.execute("CREATE TABLE IF NOT EXISTS stbchat_users (name text, nick text, permission_level integer, password text);")
            .await
            .expect("Failed to execute query");
        db
    });
}

pub async fn add_user(
    name: String,
    password: String,
) -> Result</* User created? */ bool, sqlx::Error> {
    if sqlx::query("SELECT * FROM stbchat_users WHERE name=$1")
        .bind(&name)
        .fetch_optional(&DATABASE.clone())
        .await
        .expect("Failed to execute query")
        .is_some()
    {
        return Ok(false);
    };
    sqlx::query("INSERT INTO stbchat_users (name, permission_level, password) VALUES ($1, 0, $2)")
        .bind(&name)
        .bind(sha512_hash(password))
        .execute(&DATABASE.clone())
        .await?;
    Ok(true)
}

pub async fn check_login(name: String, password: String) -> Result<bool, sqlx::Error> {
    let Some(user) =
        sqlx::query_as::<_, DatabaseRecord>("SELECT * FROM stbchat_users WHERE name=$1")
            .bind(&name)
            .fetch_optional(&DATABASE.clone())
            .await?
    else {
        return Ok(false);
    };

    return Ok(user.password == sha512_hash(password));
}
