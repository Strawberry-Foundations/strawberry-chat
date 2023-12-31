use serde::{Deserialize, Serialize};
use crate::system_core::types::{SYSTEM_MESSAGE, USER_MESSAGE};

pub struct Package {
    pub system: SystemMessage,
    pub user: UserMessage,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct SystemMessage {
    pub message_type: String,
    pub message: MessageStruct,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct UserMessage {
    pub message_type: String,
    pub message: MessageStruct,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct MessageStruct {
    pub content: String
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

    pub fn write(&mut self, message: impl ToString) -> String {
        self.message.content = message.to_string();
        self.message.content = message.to_string();

        serde_json::to_string(self).unwrap()
    }
}