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
    pub badge: String,
    pub role_color: String,
    pub avatar_url: String,
}

#[derive(Clone, Default, Debug, PartialEq, Eq)]
pub struct UserAccount {
    pub user_id: i32,
    pub username: String,
    pub password: String,
    pub nickname: String,
    pub description: String,
    pub badge: String,
    pub badges: String,
    pub avatar_url: String,
    pub role: String,
    pub role_color: String,
    pub enable_blacklisted_words: bool,
    pub account_enabled: bool,
    pub enable_dms: bool,
    pub muted: bool,
    pub strawberry_id: String,
    pub discord_name: String,
    pub msg_count: i32,
    pub creation_date: i32,
    pub ok: bool,
    pub user: User,
}