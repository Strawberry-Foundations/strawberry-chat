use tokio::net::TcpStream;
use tokio::sync::RwLock;

pub struct Registry<'a> {
    pub users: RwLock<Vec<String>>,
    pub clients: RwLock<Vec<(&'a mut TcpStream, String)>>,
}

impl Registry<'_>{
    pub fn new() -> Self {
        Self {
            users: RwLock::new(Vec::new()),
            clients: RwLock::new(Vec::new()),
        }
    }


}