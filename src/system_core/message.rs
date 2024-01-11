//! Contains messages sent internally

use crate::system_core::objects::UserObject;

#[derive(Clone, Debug)]
pub enum MessageToClient {
    UserMessage {
        author: UserObject,
        content: String,
    },
    SystemMessage {
        content: String,
    },
    Shutdown
}

pub enum MessageToServer {
    Authorize {
        user: UserObject
    },
    Message {
        content: String
    },
    RunCommand {
        name: String,
        args: Vec<String>
    },
    RemoveMe,
    ClientDisconnect {
        reason: String
    },
}