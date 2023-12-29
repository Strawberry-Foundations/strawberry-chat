use serde::{Deserialize, Serialize};

#[derive(Serialize, Deserialize, Clone, Debug)]
pub struct User {
    pub name: String,
    pub nick: String,
    pub member_since: i32,
}
