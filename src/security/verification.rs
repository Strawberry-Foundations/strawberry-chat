use sqlx::Row;
use stblib::stbm::stbchat::object::User;
use crate::database::db::DATABASE;

pub struct BlockedWords<'a> {
    pub blacklisted_words: Vec<&'a str>,
    pub content_block: Vec<&'a str>,
}

pub struct MessageVerification {
    pub blocked_words: BlockedWords<'static>,
}

#[derive(PartialEq, Eq)]
pub enum MessageAction {
    Allow,
    Hide,
    Kick,
    UserMuted
}

impl MessageVerification {
    pub async fn check(&self, content: &impl ToString) -> MessageAction {
        let content = content.to_string();
        
        if self.blocked_words.blacklisted_words.iter().any(|w| content.contains(w)) {
            return MessageAction::Kick;
        }
        if self.blocked_words.content_block.iter().any(|w| content.contains(w)) {
            return MessageAction::Hide;
        }
        if content.trim().is_empty() {
            return MessageAction::Hide;
        }
        MessageAction::Allow
    }
    
    pub async fn check_with_user(&self, content: &impl ToString, user: &User) -> MessageAction {
        let content = content.to_string();

        let user_data = sqlx::query("SELECT muted FROM users WHERE username = ?")
            .bind(&user.username)
            .fetch_all(&DATABASE.connection)
            .await.expect("err");
        
        let muted: bool = user_data.first().unwrap().get("muted");
        
        if self.blocked_words.blacklisted_words.iter().any(|w| content.contains(w)) {
            return MessageAction::Kick;
        }
        if self.blocked_words.content_block.iter().any(|w| content.contains(w)) {
            return MessageAction::Hide;
        }
        if content.trim().is_empty() {
            return MessageAction::Hide;
        }
        if muted {
            return MessageAction::UserMuted;
        }

        MessageAction::Allow
    }
}

impl MessageVerification {
    pub fn new() -> Self {
        Self {
            blocked_words: BlockedWords {
                blacklisted_words: vec!["gullideckel"],
                content_block: vec!["[#<keepalive.event.sent>]"],
            }
        }
    }
}