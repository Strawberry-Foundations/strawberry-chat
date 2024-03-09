use tokio::sync::RwLock;
use lazy_static::lazy_static;
use crate::system_core::server_core::Core;

pub mod log;
pub mod config;
pub mod login;
pub mod types;
pub mod objects;
pub mod message;
pub mod server_core;
pub mod commands;
pub mod string;
pub mod watchdog;
mod register;
mod permissions;

lazy_static! {
    pub static ref CORE: RwLock<Core> = RwLock::new(Core::new());
}