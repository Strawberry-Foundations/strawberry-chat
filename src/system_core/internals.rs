//! Contains messages sent internally

use libstrawberry::stbchat::object::User;
use crate::system_core::string::StbString;

#[derive(Clone, Debug)]
pub enum MessageToClient {
    UserMessage {
        author: User,
        content: String,
    },
    SystemMessage {
        content: String,
    },
    Notification {
        title: String,
        username: String,
        avatar_url: String,
        content: String,
        bell: bool,
    },
    Shutdown
}

#[derive(Clone, Debug)]
pub enum MessageToServer {
    Authorize {
        user: User
    },
    Message {
        content: String
    },
    Broadcast {
        content: String
    },
    RunCommand {
        name: String,
        args: Vec<String>
    },
    RemoveMe {
        username: Option<String>
    },
    ClientDisconnect {
        reason: String
    },
    SystemMessage {
        content: String
    },
    ClientNotification {
        content: StbString,
        bell: bool,
        sent_by: User
    },
}