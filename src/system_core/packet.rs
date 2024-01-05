use tokio::io::{AsyncWrite, AsyncWriteExt};

use serde::{Deserialize, Serialize};

use crate::system_core::objects::NotificationObject;
use crate::system_core::types::{STBCHAT_BACKEND, STBCHAT_EVENT, STBCHAT_NOTIFICATION, SYSTEM_MESSAGE, USER_MESSAGE};
use crate::system_core::user::UserObject;

/// # Packet Handling
/// - Struct `Packet`: Packet Object to create multiple packets at once
/// - Struct `SystemMessage`: `system_message` Data type
/// - Struct `UserMessage`: `user_message` Data type
/// - Struct `NotificationBackend`: `stbchat_notification` Data type
/// - Struct `ClientBackend`: `stbchat_backend` Data type
/// - Struct `EventBackend`: `stbchat_event` Data type
/// - Struct `MessageStruct`: general sub data type for all *message types
/// - Struct `UserMetaStruct`: general sub data type for all meta-specific types

pub struct Packet {
    pub system: SystemMessage,
    pub user: UserMessage,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct MessageStruct {
    pub content: String,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct UserMetaStruct {
    pub username: String,
}


#[derive(Debug, Serialize, Deserialize)]
pub struct SystemMessage {
    pub message_type: String,
    pub message: MessageStruct,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct UserMessage {
    pub message_type: String,
    pub username: String,
    pub nickname: String,
    pub badge: char,
    pub role_color: String,
    pub avatar_url: String,
    pub message: MessageStruct,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct NotificationBackend {
    pub message_type: String,
    pub title: String,
    pub username: String,
    pub avatar_url: String,
    pub content: String,
    pub bell: bool,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct ClientBackend {
    pub message_type: String,
    pub user_meta: UserMetaStruct,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct EventBackend {
    pub message_type: String,
    pub event_type: String,
}

/// # `SystemMessage` Implementation
/// - Implements the data type `system_message`
impl SystemMessage {
    pub fn new<M: ToString>(content: &M) -> Self {
        Self {
            message_type: SYSTEM_MESSAGE.to_string(),
            message: MessageStruct {
                content: content.to_string()
            }
        }
    }

    pub async fn write<W: AsyncWrite + Unpin>(&mut self, target: &mut W) -> tokio::io::Result<()> {
        target.write_all(serde_json::to_string(self).unwrap().as_bytes()).await
    }
}

/// # `UserMessage` Implementation
/// - Implements the data type `user_message`
impl UserMessage {
    pub fn new<M: ToString>(author: UserObject, message: &M) -> Self {
        Self {
            message_type: USER_MESSAGE.to_string(),
            username: author.username,
            nickname: author.nickname,
            badge: author.badge,
            role_color: author.role_color,
            avatar_url: author.avatar_url,
            message: MessageStruct {
                content: message.to_string()
            },
        }
    }

    pub async fn write<W: AsyncWrite + Unpin>(&mut self, target: &mut W) -> tokio::io::Result<()> {
        target.write_all(serde_json::to_string(self).unwrap().as_bytes()).await
    }
}

/// # `NotificationBackend` Implementation
/// - Implements the data type `stbchat_notification`
impl NotificationBackend {
    pub fn new<M: ToString>(notification: NotificationObject, message: &M) -> Self {
        Self {
            message_type: STBCHAT_NOTIFICATION.to_string(),
            title: notification.title,
            username: notification.username,
            avatar_url: notification.avatar_url,
            content: message.to_string(),
            bell: notification.bell,
        }
    }

    pub async fn write<W: AsyncWrite + Unpin>(&mut self, target: &mut W) -> tokio::io::Result<()> {
        target.write_all(serde_json::to_string(self).unwrap().as_bytes()).await
    }
}

/// # `ClientBackend` Implementation
/// - Implements the data type `stbchat_backend`
impl ClientBackend {
    pub fn new<U: ToString>(username: &U) -> Self {
        Self {
            message_type: STBCHAT_BACKEND.to_string(),
            user_meta: UserMetaStruct {
                username: username.to_string(),
            },
        }
    }

    pub async fn write<W: AsyncWrite + Unpin>(&mut self, target: &mut W) -> tokio::io::Result<()> {
        target.write_all(serde_json::to_string(self).unwrap().as_bytes()).await
    }
}

/// # `EventBackend` Implementation
/// - Implements the data type `stbchat_event`
impl EventBackend {
    pub fn new<E: ToString>(event: &E) -> Self {
        Self {
            message_type: STBCHAT_EVENT.to_string(),
            event_type: event.to_string(),
        }
    }

    pub fn push(&mut self) -> String {
        serde_json::to_string(self).unwrap()
    }

    pub async fn write<W: AsyncWrite + Unpin>(&mut self, target: &mut W) -> tokio::io::Result<()> {
        target.write_all(serde_json::to_string(self).unwrap().as_bytes()).await
    }
}