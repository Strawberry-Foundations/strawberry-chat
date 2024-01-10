pub struct NotificationObject {
    pub title: String,
    pub username: String,
    pub avatar_url: String,
    pub bell: bool
}

pub struct ClientLoginCredentialsPacket {
    pub username: String,
    pub password: String,
}

impl ClientLoginCredentialsPacket {
    pub const fn new() -> Self {
        Self {
            username: String::new(),
            password: String::new(),
        }
    }
}