use std::collections::HashMap;

pub struct UserStatus {
    pub users: HashMap<String, Status>
}

#[derive(Copy, Clone, Eq, PartialEq, Default)]
pub enum Status {
    #[default]
    Online,
    DoNotDisturb,
    Afk,
    Offline
}

impl UserStatus {
    pub fn new() -> Self {
        Self {
            users: HashMap::new()
        }
    }

    pub fn append(&mut self, username: &str, status: Status) {
        self.users.insert(username.to_string(), status).unwrap();
    }

    pub fn get_by_name(&self, username: &str) -> &Status {
        self.users.get(username).unwrap()
    }
}