//! Contains messages sent internally

use crate::system_core::user::UserObject;

pub enum MessageToClient {
    UserMessage {
        author: UserObject,
        content: String
    }
}

pub enum MessageToServer {
    Message {
        content: String
    },
    RemoveMe
}