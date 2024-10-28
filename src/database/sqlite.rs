use eyre::eyre;
use sqlx::{SqlitePool, Sqlite, Pool, Row};

use stblib::stbchat::object::User;
use stblib::utilities::unix_time;

use crate::system_core::log::log_parser;
use crate::system_core::objects::{Account, UserAccount};
use crate::constants::types::CRTLCODE_CLIENT_EXIT;
use crate::constants::log_messages::DATABASE_CONNECTION_ERROR;
use crate::database::Database;
use crate::global::{CONFIG, RUNTIME_LOGGER};
use crate::security::crypt::Crypt;
use crate::utilities::role_color_parser;

pub struct SQLiteDB {
    pub connection: Pool<Sqlite>
}

#[async_trait::async_trait]
impl Database for SQLiteDB {
    async fn hello(&self) {
        let _ = &self.connection;

        let row: (bool,) = sqlx::query_as(
            "SELECT EXISTS (
            SELECT 1
            FROM sqlite_master
            WHERE type = 'table'
              AND name = ?
            )")
            .bind(&CONFIG.database.table)
            .fetch_one(&self.connection)
            .await.unwrap();

        if !row.0 {
            RUNTIME_LOGGER.default(format!("Table '{}' does not exists. Creating ...", CONFIG.database.table));
            self.initialize_table().await;
        }

        match sqlx::query(format!("SELECT username FROM {}", CONFIG.database.table).as_str())
            .execute(&self.connection)
            .await {
            Ok(_) => (),
            Err(err) => {
                RUNTIME_LOGGER.panic_crash(format!("Database error: {err}"));
            }
        };
    }

    async fn initialize_table(&self) {
        sqlx::query(r#"CREATE TABLE "users" (
            "user_id"	INTEGER,
            "username"	TEXT,
            "password"	TEXT,
            "nickname"	TEXT,
            "description"	TEXT,
            "badge"	TEXT,
            "badges"	TEXT,
            "avatar_url"	TEXT,
            "role"	TEXT,
            "role_color"	TEXT,
            "enable_blacklisted_words"	INTEGER,
            "account_enabled"	INTEGER,
            "enable_dms"	INTEGER,
            "muted"	INTEGER,
            "strawberry_id"	TEXT,
            "discord_name"	TEXT,
            "blocked"	TEXT,
            "msg_count"	INTEGER,
            "creation_date"	INTEGER
            );"#)
            .execute(&self.connection)
            .await
            .unwrap_or_else(|err| RUNTIME_LOGGER.panic_crash(format!("Table creation failed: {err}")));
    }

    #[allow(clippy::cast_possible_wrap)]
    async fn create_user(&self, user_id: i64, username: String, password: String, role_color: String) {
        let creation_date = unix_time() as i64;
        sqlx::query(format!("INSERT INTO {} (\
            user_id, \
            username, \
            password, \
            nickname, \
            description, \
            badge, \
            badges, \
            avatar_url, \
            role, \
            role_color, \
            enable_blacklisted_words, \
            account_enabled, \
            enable_dms, \
            muted, \
            strawberry_id, \
            discord_name, \
            blocked, \
            msg_count, \
            creation_date \
            ) \
            VALUES (\
            ?, \
            ?, \
            ?, \
            '', \
            '', \
            '', \
            '', \
            '', \
            'member', \
            ?, \
            1, 1, 1, 0, '', '', '', 0, ?);", CONFIG.database.table).as_str())
            .bind(user_id)
            .bind(username)
            .bind(password)
            .bind(role_color)
            .bind(creation_date)
            .execute(&self.connection)
            .await.unwrap();
    }

    async fn delete_user(&self, username: String) {
        sqlx::query(format!("DELETE FROM {} WHERE username = ?", CONFIG.database.table).as_str())
            .bind(username)
            .execute(&self.connection)
            .await.unwrap();
    }

    async fn check_credentials(&self, username: &'_ str, entered_password: &'_ str) -> (UserAccount, bool) {
        let row = sqlx::query(format!("SELECT username, password FROM {} WHERE username = ?", CONFIG.database.table).as_str())
            .bind(username)
            .fetch_all(&self.connection)
            .await.expect("err");

        if row.is_empty() {
            return (UserAccount::default(), false)
        }

        let stored_password: String = row.first().unwrap().get("password");

        if !Crypt::verify_password(stored_password.as_str(), &entered_password.to_string()) {
            return (UserAccount::default(), false)
        }

        let mut user = User {
            username: CRTLCODE_CLIENT_EXIT.to_string(),
            nickname: String::new(),
            badge: String::new(),
            role_color: String::new(),
            avatar_url: String::new(),
        };

        let data = sqlx::query(format!("SELECT * FROM {} WHERE username = ?", CONFIG.database.table).as_str())
            .bind(username)
            .fetch_all(&self.connection)
            .await.expect("err");

        let nickname: String = data.first().unwrap().get("nickname");

        user.username   = data.first().unwrap().get("username");
        user.nickname   = data.first().unwrap().get("nickname");
        user.badge      = data.first().unwrap().get("badge");
        user.role_color = role_color_parser(data.first().unwrap().get("role_color"));
        user.avatar_url = data.first().unwrap().get("avatar_url");

        if nickname.is_empty() {
            user.nickname.clone_from(&user.username);
        }
        else {
            user.nickname = data.first().unwrap().get("nickname");
        }

        let user_account = UserAccount {
            user_id: data.first().unwrap().get("user_id"),
            username: data.first().unwrap().get("username"),
            password: data.first().unwrap().get("password"),
            nickname: data.first().unwrap().get("nickname"),
            description: data.first().unwrap().get("description"),
            badge: data.first().unwrap().get("badge"),
            badges: data.first().unwrap().get("badges"),
            avatar_url: data.first().unwrap().get("avatar_url"),
            role: data.first().unwrap().get("role"),
            role_color: data.first().unwrap().get("role_color"),
            enable_blacklisted_words: data.first().unwrap().get("enable_blacklisted_words"),
            account_enabled: data.first().unwrap().get("account_enabled"),
            enable_dms: data.first().unwrap().get("enable_dms"),
            muted: data.first().unwrap().get("muted"),
            strawberry_id: data.first().unwrap().get("strawberry_id"),
            discord_name: data.first().unwrap().get("discord_name"),
            blocked: data.first().unwrap().get("blocked"),
            msg_count: data.first().unwrap().get("msg_count"),
            creation_date: data.first().unwrap().get("creation_date"),
            ok: data.first().unwrap().get("account_enabled"),
            user
        };

        (user_account, true)
    }

    async fn is_username_taken(&self, username: &'_ str) -> bool {
        let query = sqlx::query(format!("SELECT username FROM {} WHERE username = ?", CONFIG.database.table).as_str())
            .bind(username)
            .fetch_optional(&self.connection)
            .await.unwrap();

        query.is_some()
    }

    async fn is_account_enabled(&self, username: &'_ str) -> Option<bool> {
        let query: Option<bool> = sqlx::query_scalar(format!("SELECT account_enabled FROM {} WHERE username = ?", CONFIG.database.table).as_str())
            .bind(username)
            .fetch_optional(&self.connection)
            .await.unwrap();

        query
    }

    async fn is_user_muted(&self, username: &'_ str) -> Option<bool> {
        let query: Option<bool> = sqlx::query_scalar(format!("SELECT muted FROM {} WHERE username = ?", CONFIG.database.table).as_str())
            .bind(username)
            .fetch_optional(&self.connection)
            .await.unwrap();

        query
    }

    async fn get_members(&self) -> Vec<String> {
        sqlx::query_scalar(format!("SELECT username from {}", CONFIG.database.table).as_str())
            .fetch_all(&self.connection)
            .await.unwrap()
    }

    async fn get_members_by_role(&self, role: &'_ str) -> Vec<String> {
        sqlx::query_scalar(format!("SELECT username, badge FROM {} WHERE role = '{role}'", CONFIG.database.table).as_str())
            .fetch_all(&self.connection)
            .await.unwrap()
    }

    async fn get_next_user_id(&self) -> i64 {
        #[derive(sqlx::FromRow)]
        struct QUser {
            user_id: i64,
        }

        let query = sqlx::query_as::<_, QUser>(format!("SELECT user_id FROM {} ORDER BY user_id DESC LIMIT 1", CONFIG.database.table).as_str())
            .fetch_optional(&self.connection)
            .await.unwrap();

        query.map_or(1, |user| user.user_id + 1)
    }

    async fn get_user_by_name(&self, username: &'_ str) -> Option<User> {
        let data = sqlx::query(format!("SELECT * FROM {} WHERE username = ?", CONFIG.database.table).as_str())
            .bind(username)
            .fetch_all(&self.connection)
            .await.expect("err");

        if data.is_empty() {
            None
        }
        else {
            let mut user = User {
                username: CRTLCODE_CLIENT_EXIT.to_string(),
                nickname: String::new(),
                badge: String::new(),
                role_color: String::new(),
                avatar_url: String::new(),
            };

            user.username   = data.first().unwrap().get("username");
            user.nickname   = data.first().unwrap().get("nickname");
            user.badge      = data.first().unwrap().get("badge");
            user.role_color = role_color_parser(data.first().unwrap().get("role_color"));
            user.avatar_url = data.first().unwrap().get("avatar_url");

            Some(user)
        }
    }

    async fn get_account_by_name(&self, username: &'_ str) -> Option<Account> {
        let data: Vec<Account> = sqlx::query_as(format!("SELECT * FROM {} WHERE LOWER(username) = ?", CONFIG.database.table).as_str())
            .bind(username.to_lowercase())
            .fetch_all(&self.connection)
            .await.expect("err");

        if data.is_empty() {
            None
        }

        else {
            data.first().map(std::borrow::ToOwned::to_owned)
        }
    }

    async fn get_blocked_from_user(&self, username: &'_ str) -> String {
        sqlx::query(format!("SELECT blocked FROM {} WHERE username = ?", CONFIG.database.table).as_str())
            .bind(username)
            .fetch_one(&self.connection)
            .await.unwrap().get("blocked")
    }

    async fn get_val_from_user(&self, username: &'_ str, value: &'_ str) -> Option<String> {
        let user_data = sqlx::query(format!("SELECT {value} FROM {} WHERE LOWER(username) = ?", CONFIG.database.table).as_str())
            .bind(username.to_lowercase())
            .fetch_all(&self.connection)
            .await.expect("err");

        if user_data.is_empty() {
            None
        }
        else {
            user_data.first().unwrap().get(value)
        }
    }

    async fn update_val(&self, username: &'_ str, key: &'_ str, value: &'_ str) -> eyre::Result<()> {
        match sqlx::query(format!("UPDATE {} SET {key} = ? WHERE username = ?", CONFIG.database.table).as_str())
            .bind(value)
            .bind(username)
            .execute(&self.connection)
            .await {
            Ok(..) => Ok(()),
            Err(_) => Err(eyre!(""))
        }
    }
}

impl SQLiteDB {
    pub async fn new(url: &str) -> Self {
        let connection = SqlitePool::connect(url).await.unwrap_or_else(|err| {
            RUNTIME_LOGGER.panic_crash(log_parser(DATABASE_CONNECTION_ERROR, &[&err]));
        });

        Self {
            connection
        }
    }
}