//! Contains messages sent internally

use crate::system_core::user::UserObject;

#[derive(Clone)]
pub enum MessageToClient {
    UserMessage {
        author: UserObject,
        content: String
    }
}

pub enum MessageToServer {
    Authorize {
        user: UserObject
    },
    Message {
        content: String
    },
    RemoveMe
}