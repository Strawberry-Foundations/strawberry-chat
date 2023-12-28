use stbchat::user::User;

pub enum MessageToClient {
    UserMessage { user: User, content: String },
    SystemMessage { content: String },
}

pub enum MessageFromClient {
    Authenticated { user: User },
    Message { content: String },
    RunCommand { command: String, args: Vec<String> },
}
