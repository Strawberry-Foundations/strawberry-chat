#![allow(clippy::future_not_send)]

use serde::{Deserialize, Serialize};
use crate::object::User;

/// # A packet sent from the server to the client (S -> C)
/// - `SystemMessage`: A message sent from the system
/// - `UserMessage`: A message sent from a user
/// - `NotificationBackend`: Tells the client to show a notification
/// - `ClientBackend`: Data type
#[derive(Serialize, Deserialize)]
#[serde(tag = "packet_type")]
pub enum ClientboundPacket {
    #[serde(rename = "system_message")]
    SystemMessage {
        message: MessageStruct
    },
    #[serde(rename = "user_message")]
    UserMessage {
        author: User,
        message: MessageStruct,
    },
    #[serde(rename = "notification_backend")]
    Notification {
        title: String,
        username: String,
        avatar_url: String,
        content: String,
        bell: bool,
    },
    #[serde(rename = "stbchat_backend")]
    BackendMessage {
        event_type: String,
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
        message: MessageStruct
    }
}

#[derive(Debug, Serialize, Deserialize)]
pub struct MessageStruct {
    pub content: String,
}

impl MessageStruct {
    pub fn new(msg: impl ToString) -> Self {
        Self { content: msg.to_string() }
    }
}

#[derive(Debug, Serialize, Deserialize)]
pub struct UserMetaStruct {
    pub username: String,
}