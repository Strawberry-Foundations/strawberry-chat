use serde::{Deserialize, Serialize};
use crate::system_core::types::{SYSTEM_MESSAGE, USER_MESSAGE};
use crate::system_core::user::UserObject;

/// # Package Handling
/// - Struct `Package`: Package Object to create multiple packages at once
/// - Struct `SystemMessage`: `system_message` Data type
/// - Struct `UserMessage`: `user_message` Data type
/// - Struct `NotificationBackend`: `stbchat_notification` Data type
/// - Struct `MessageStruct`: general sub data type for all *message types

pub struct Package {
    pub system: SystemMessage,
    pub user: UserMessage,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct MessageStruct {
    pub content: String
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



impl Package {
    pub fn new() -> Self {
        Self {
            system: SystemMessage {
                message_type: SYSTEM_MESSAGE.to_string(),
                message: MessageStruct {
                    content: String::new()
                }
            },
            user: UserMessage {
                message_type: USER_MESSAGE.to_string(),
                username: String::new(),
                nickname: String::new(),
                badge: '\x00',
                role_color: String::new(),
                avatar_url: String::new(),
                message: MessageStruct {
                    content: String::new()
                },
            },
        }
    }
}

impl SystemMessage {
    pub fn new() -> Self {
        Self {
            message_type: SYSTEM_MESSAGE.to_string(),
            message: MessageStruct {
                content: String::new()
            }
        }
    }

    pub fn write(&mut self, message: &impl ToString) -> String {
        self.message.content = message.to_string();
        serde_json::to_string(self).unwrap()
    }
}

impl UserMessage {
    pub fn new() -> Self {
        Self {
            message_type: USER_MESSAGE.to_string(),
            username: String::new(),
            nickname: String::new(),
            badge: '\x00',
            role_color: String::new(),
            avatar_url:  String::new(),
            message: MessageStruct {
                content: String::new()
            },
        }
    }

    pub fn write(&mut self, user_object: UserObject, message: &impl ToString) -> String {
        self.username   = user_object.username;
        self.nickname   = user_object.nickname;
        self.badge      = user_object.badge;
        self.role_color = user_object.role_color;
        self.avatar_url = user_object.avatar_url;

        self.message.content = message.to_string();


        serde_json::to_string(self).unwrap()
    }
}