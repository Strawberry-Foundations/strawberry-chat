pub mod db;

use sqlx::{MySql, MySqlPool, Pool, Row};

use crate::constants::log_messages::SQL_CONNECTION_ERROR;
use crate::global::{RUNTIME_LOGGER};
use crate::system_core::log::log_parser;
use crate::system_core::objects::{User, UserAccount};
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

    pub async fn check_credentials(&self, username: &String, password: &String) -> UserAccount {
        let row  = sqlx::query("SELECT username, password FROM users WHERE username = ?")
            .bind(username)
            .fetch_all(&self.connection)
            .await.expect("err");

        if row.is_empty() {
            return UserAccount::default()
        }

        let db_password: String = row.first().unwrap().get("password");

        if &db_password != password {
            return UserAccount::default()
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

        user_account
    }
}