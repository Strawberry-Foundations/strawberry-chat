#![allow(clippy::future_not_send)]

use serde::{Deserialize, Serialize};
use crate::object::User;

/// # A packet sent from the server to the client (S -> C)
/// - `SystemMessage`: A message sent from the system
/// - `UserMessage`: A message sent from a user
/// - `Notification`: Tells the client to show a notification
/// - `Backend`: Sends the username to the client
#[derive(Serialize, Deserialize)]
#[serde(tag = "packet_type")]
pub enum ClientboundPacket {
    #[serde(rename = "system_message")]
    SystemMessage {
        message: Message
    },
    #[serde(rename = "user_message")]
    UserMessage {
        author: User,
        message: Message,
    },
    #[serde(rename = "notification_backend")]
    Notification {
        title: String,
        username: String,
        avatar_url: String,
        content: String,
        bell: bool,
    },
    #[serde(rename = "stbchat_event")]
    Event {
        event_type: String,
    },
    #[serde(rename = "stbchat_backend")]
    Backend {
        user_meta: UserMeta
    }
}

#[derive(Serialize, Deserialize)]
#[serde(tag = "packet_type")]
pub enum ServerboundPacket {
    Login {
        username: String,
        password: String
    },
    Message {
        message: Message
    }
}

#[derive(Debug, Serialize, Deserialize)]
pub struct Message {
    pub content: String,
}

impl Message {
    pub fn new(msg: impl ToString) -> Self {
        Self { content: msg.to_string() }
    }
}

#[derive(Debug, Serialize, Deserialize)]
pub struct UserMeta {
    pub username: String,
}