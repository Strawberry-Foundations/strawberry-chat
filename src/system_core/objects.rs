// Object for sending Notifications
pub struct NotificationObject {
    pub title: String,
    pub username: String,
    pub avatar_url: String,
    pub bell: bool
}

// Server-side object/packet for understanding the received login packet from the client
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

// General User Object for all types of user-specified code
#[derive(Clone, Default, Debug, PartialEq, Eq)]
pub struct User {
    pub username: String,
    pub nickname: String,
    pub badge: char,
    pub role_color: String,
    pub avatar_url: String,
}