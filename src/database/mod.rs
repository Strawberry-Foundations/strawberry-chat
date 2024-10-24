pub mod db;

use sqlx::{MySql, MySqlPool, Pool, Row};
use sqlx::mysql::MySqlRow;

use stblib::stbchat::object::User;
use stblib::utilities::unix_time;

use crate::system_core::log::log_parser;
use crate::system_core::objects::{Account, UserAccount};
use crate::constants::types::CRTLCODE_CLIENT_EXIT;
use crate::constants::log_messages::SQL_CONNECTION_ERROR;
use crate::global::RUNTIME_LOGGER;
use crate::security::crypt::Crypt;
use crate::utilities::role_color_parser;


pub struct Database {
    pub connection: Pool<MySql>
}

impl Database {
    pub async fn new(url: &str) -> Self {
        let connection = MySqlPool::connect(url).await.unwrap_or_else(|err| {
            RUNTIME_LOGGER.panic_crash(log_parser(SQL_CONNECTION_ERROR, &[&err]));
        });

        Self {
            connection
        }
    }
    
    pub async fn new_user(&self, user_id: i64, username: String, password: String, role_color: String) {
        sqlx::query(
            "INSERT INTO data.users (\
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
            1, 1, 1, 0, '', '', '', 0, ?);")
            .bind(user_id)
            .bind(username)
            .bind(password)
            .bind(role_color)
            .bind(unix_time())
            .execute(&self.connection)
            .await.unwrap();
    }

    pub async fn delete_user(&self, username: String) {
        sqlx::query("DELETE FROM users WHERE username = ?")
            .bind(username)
            .execute(&self.connection)
            .await.unwrap();
    }
    
    pub async fn fetch_members(&self) -> Vec<MySqlRow>{
        sqlx::query("SELECT username from users")
            .fetch_all(&self.connection)
            .await.unwrap()
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

        if !Crypt::verify_password(stored_password.as_str(), entered_password) {
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

    pub async fn is_username_taken(&self, username: &String) -> bool {
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

    pub async fn get_user_by_name(&self, username: &String) -> Option<User> {
        let data = sqlx::query("SELECT * FROM users WHERE username = ?")
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

    pub async fn get_account_by_name(&self, username: &String) -> Option<Account> {
        let data: Vec<Account> = sqlx::query_as("SELECT * FROM users WHERE username = ?")
            .bind(username)
            .fetch_all(&self.connection)
            .await.expect("err");

        if data.is_empty() {
            None
        }

        else {
            data.first().map(std::borrow::ToOwned::to_owned)
        }
    }
}