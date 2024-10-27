use std::fs::File;
use std::io::Read;
use std::path::{Path, PathBuf};

use serde::Deserialize;
use sqlx::Row;

use stblib::stbchat::object::User;

use crate::database::DATABASE;
use crate::global::{CONFIG, LOGGER};

#[derive(Deserialize)]
pub struct BlockedWords {
    pub blacklist: Vec<String>,
    pub content_block: Vec<String>,
}

pub struct MessageVerification {
    pub bad_words: BlockedWords,
}

#[derive(PartialEq, Eq)]
pub enum MessageAction {
    Allow,
    Hide,
    Kick,
    UserMuted,
    TooLong
}

impl MessageVerification {
    pub fn check(&self, content: &impl ToString) -> MessageAction {
        let content = content.to_string();

        if self.bad_words.blacklist.iter().any(|w| content.contains(w)) {
            return MessageAction::Kick;
        }
        if self.bad_words.content_block.iter().any(|w| content.contains(w)) {
            return MessageAction::Hide;
        }
        if content.trim().is_empty() {
            return MessageAction::Hide;
        }
        if content.len() > CONFIG.config.max_message_length {
            return MessageAction::TooLong;
        }
        MessageAction::Allow
    }

    pub async fn check_with_user(&self, content: &String, user: &User) -> MessageAction {
        let content = content.to_string();
        let muted = DATABASE.is_user_muted(&user.username.as_str()).await;

        if self.bad_words.blacklist.iter().any(|w| content.contains(w)) {
            return MessageAction::Kick;
        }
        if self.bad_words.content_block.iter().any(|w| content.contains(w)) {
            return MessageAction::Hide;
        }
        if content.trim().is_empty() {
            return MessageAction::Hide;
        }
        if content.len() > CONFIG.config.max_message_length {
            return MessageAction::TooLong;
        }
        if muted {
            return MessageAction::UserMuted;
        }

        MessageAction::Allow
    }
}

impl MessageVerification {
    pub fn new() -> Self {
        let exe_path = std::env::current_exe().unwrap();
        let exe_dir = exe_path.parent().unwrap();
        let exe_dir_str = PathBuf::from(exe_dir).display().to_string();

        let mut bad_words_path = format!("{exe_dir_str}/bad_words.yml");

        if !Path::new(&bad_words_path).exists() {
            bad_words_path = String::from("./bad_words.yml");
        }

        let mut file = File::open(bad_words_path).unwrap_or_else(|err| {
           LOGGER.critical_panic(format!("Could not read bad words: {err}"))
        });

        let mut contents = String::new();
        file.read_to_string(&mut contents).unwrap_or_else(|err| {
            LOGGER.critical_panic(format!("Could not read bad words: {err}"))
        });
        
        let bad_words: BlockedWords = serde_yaml::from_str(&contents).unwrap_or_else(|err| {
            LOGGER.critical_panic(format!("Could not read bad words: {err}"))
        });

        Self {
            bad_words
        }
    }
}