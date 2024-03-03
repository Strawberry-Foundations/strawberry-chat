//! Contains messages sent internally

use stblib::stbm::stbchat::object::User;

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
    RemoveMe,
    ClientDisconnect {
        reason: String
    },
}