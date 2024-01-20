pub mod db;

use sqlx::{MySql, MySqlPool, Pool, Row};

use crate::constants::log_messages::SQL_CONNECTION_ERROR;
use crate::global::{RUNTIME_LOGGER};
use crate::system_core::log::log_parser;
use crate::system_core::objects::User;
use crate::system_core::types::CRTLCODE_CLIENT_EXIT;
use crate::utilities::role_color_parser;

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

    pub async fn check_credentials(&self, username: &String, password: &String) -> User {
        let row  = sqlx::query("SELECT username, password FROM users WHERE username = ?")
            .bind(username)
            .fetch_all(&self.connection)
            .await.expect("err");

        if row.is_empty() {
            return User {
                username: CRTLCODE_CLIENT_EXIT.to_string(),
                nickname: String::new(),
                ..Default::default()
            };
        }

        let db_password: String = row.first().unwrap().get("password");

        if &db_password != password {
            return User {
                username: CRTLCODE_CLIENT_EXIT.to_string(),
                nickname: String::new(),
                ..Default::default()
            };
        }

        let mut user = User {
            username: CRTLCODE_CLIENT_EXIT.to_string(),
            nickname: String::new(),
            badge: String::new(),
            role_color: String::new(),
            avatar_url: String::new(),
        };

        let data = sqlx::query("SELECT username, nickname, badge, role_color, avatar_url FROM users WHERE username = ?")
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

        user
    }
}