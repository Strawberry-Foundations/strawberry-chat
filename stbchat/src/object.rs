use serde::{Deserialize, Serialize};

// General User Object for all types of user-specified code
#[derive(Clone, Default, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct User {
    pub username: String,
    pub nickname: String,
    pub badge: String,
    pub role_color: String,
    pub avatar_url: String,
}