pub mod db;

use sqlx::{MySql, MySqlPool, Pool, Row};
use argon2::{Argon2, PasswordHash, PasswordHasher, PasswordVerifier};
use argon2::password_hash::rand_core::OsRng;
use argon2::password_hash::SaltString;
use stblib::stbm::stbchat::object::User;

use crate::constants::log_messages::SQL_CONNECTION_ERROR;
use crate::global::RUNTIME_LOGGER;
use crate::system_core::log::log_parser;
use crate::system_core::objects::UserAccount;
use crate::system_core::types::CRTLCODE_CLIENT_EXIT;
use crate::utilities::role_color_parser;

pub struct Database {
    pub connection: Pool<MySql>
}

impl Database {
    pub async fn new(url: &str) -> Self {
        let connection = MySqlPool::connect(url).await.unwrap_or_else(|err| {
            RUNTIME_LOGGER.panic(log_parser(SQL_CONNECTION_ERROR, &[&err]));
        });

        Self {
            connection
        }
    }

    pub fn verify_password(stored_password: &str, entered_password: &String) -> bool {
        let hash = PasswordHash::new(stored_password).unwrap();

        let password: &[u8] = entered_password.as_bytes();

        Argon2::default().verify_password(password, &hash).is_ok()
    }

    pub fn hash_password(plain_password: String) -> String {
        let argon2 = Argon2::default();
        let salt = SaltString::generate(&mut OsRng);

        let hashed_password = argon2.hash_password(plain_password.as_bytes(), &salt).unwrap();
        hashed_password.to_string()
    }

    pub async fn check_credentials(&self, username: &String, entered_password: &String) -> (UserAccount, bool) {
        let row = sqlx::query("SELECT username, password FROM users WHERE username = ?")
            .bind(username)
            .fetch_all(&self.connection)
            .await.expect("err");

        if row.is_empty() {
            return (UserAccount::default(), false)
        }

        let stored_password: String = row.first().unwrap().get("password");

        if !Self::verify_password(stored_password.as_str(), entered_password) {
            return (UserAccount::default(), false)
        }

        let mut user = User {
            username: CRTLCODE_CLIENT_EXIT.to_string(),
            nickname: String::new(),
            badge: String::new(),
            role_color: String::new(),
            avatar_url: String::new(),
        };

        let data = sqlx::query("SELECT * FROM users WHERE username = ?")
            .bind(username)
            .fetch_all(&self.connection)
            .await.expect("err");

        let nickname: String = data.first().unwrap().get("nickname");

        user.username   = data.first().unwrap().get("username");
        user.nickname   = data.first().unwrap().get("nickname");
        user.badge      = data.first().unwrap().get("badge");
        user.role_color = role_color_parser(data.first().unwrap().get("role_color"));
        user.avatar_url = data.first().unwrap().get("avatar_url");

        if nickname.is_empty(){
            user.nickname = user.username.clone();
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
            msg_count: data.first().unwrap().get("msg_count"),
            creation_date: data.first().unwrap().get("creation_date"),
            ok: data.first().unwrap().get("account_enabled"),
            user
        };

        (user_account, true)
    }

    pub async fn is_username_taken(&self, username: String) -> bool {
        let query = sqlx::query("SELECT username FROM users WHERE username = ?")
            .bind(username)
            .fetch_optional(&self.connection)
            .await.unwrap();

        query.is_some()
    }

    pub async fn get_next_user_id(&self) -> i64 {
        #[derive(sqlx::FromRow)]
        struct QUser {
            user_id: i64,
        }
        
        let query = sqlx::query_as::<_, QUser>("SELECT user_id FROM users ORDER BY user_id DESC LIMIT 1")
            .fetch_optional(&self.connection)
            .await.unwrap();

        query.map_or(1, |user| user.user_id + 1)
    }
}