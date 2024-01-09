#[derive(Clone, Default, Debug)]
pub struct UserObject {
    pub username: String,
    pub nickname: String,
    pub badge: char,
    pub role_color: String,
    pub avatar_url: String,
}