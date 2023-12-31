use serde::{Deserialize, Serialize};
use crate::system_core::objects::NotificationObject;
use crate::system_core::types::{LOGIN_EVENT, STBCHAT_BACKEND, STBCHAT_EVENT, STBCHAT_NOTIFICATION, SYSTEM_MESSAGE, USER_MESSAGE};
use crate::system_core::user::UserObject;

/// # Package Handling
/// - Struct `Package`: Package Object to create multiple packages at once
/// - Struct `SystemMessage`: `system_message` Data type
/// - Struct `UserMessage`: `user_message` Data type
/// - Struct `NotificationBackend`: `stbchat_notification` Data type
/// - Struct `ClientBackend`: `stbchat_backend` Data type
/// - Struct `EventBackend`: `stbchat_event` Data type
/// - Struct `MessageStruct`: general sub data type for all *message types
/// - Struct `UserMetaStruct`: general sub data type for all meta-specific types

pub struct Package {
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

/// # Main Package Implementation
/// - Implements System and User messages with one internal Object

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

/// # `SystemMessage` Implementation
/// - Implements the data type `system_message`
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

/// # `UserMessage` Implementation
/// - Implements the data type `user_message`
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

/// # `NotificationBackend` Implementation
/// - Implements the data type `stbchat_notification`
    impl NotificationBackend {
    pub fn new() -> Self {
        Self {
            message_type: STBCHAT_NOTIFICATION.to_string(),
            title: String::new(),
            username: String::new(),
            avatar_url: String::new(),
            content: String::new(),
            bell: false,
        }
    }

    pub fn write(&mut self, notification_object: NotificationObject, message: &impl ToString) -> String {
        self.title      = notification_object.title;
        self.username   = notification_object.username;
        self.avatar_url = notification_object.avatar_url;
        self.content    = message.to_string();
        self.bell       = notification_object.bell;

        serde_json::to_string(self).unwrap()
    }
}

/// # `ClientBackend` Implementation
/// - Implements the data type `stbchat_backend`
impl ClientBackend {
    pub fn new() -> Self {
        Self {
            message_type: STBCHAT_BACKEND.to_string(),
            user_meta: UserMetaStruct {
                username: String::new(),
            },
        }
    }

    pub fn write(&mut self, username: &impl ToString) -> String {
        self.user_meta.username = username.to_string();

        serde_json::to_string(self).unwrap()
    }
}

/// # `EventBackend` Implementation
/// - Implements the data type `stbchat_event`
impl EventBackend {
    pub fn new() -> Self {
        Self {
            message_type: STBCHAT_EVENT.to_string(),
            event_type: String::new(),
        }
    }

    pub fn write(&mut self, event: &impl ToString) -> String {
        self.event_type = event.to_string();

        serde_json::to_string(self).unwrap()
    }
}