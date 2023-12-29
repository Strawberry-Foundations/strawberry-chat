use stbchat::user::User;

#[derive(Debug)]
pub enum MessageToClient {
    ReceiveUserMessage { user: User, content: String },
    ReceiveSystemMessage { content: String },
    Disconnect { reason: String },
}

#[derive(Debug)]
pub enum MessageFromClient {
    Authenticated { user: User },
    SentMessage { content: String },
    RanCommand { command: String, args: Vec<String> },
    RemoveMe,
}
