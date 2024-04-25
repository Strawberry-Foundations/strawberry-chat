use tokio::sync::RwLock;
use lazy_static::lazy_static;
use crate::system_core::server_core::Core;

pub mod log;
pub mod config;
pub mod login;
pub mod objects;
pub mod internals;
pub mod server_core;
pub mod commands;
pub mod string;
pub mod watchdog;
pub mod register;
pub mod permissions;
pub mod panic;
pub mod hooks;
pub mod status;

lazy_static! {
    pub static ref CORE: RwLock<Core> = RwLock::new(Core::new());
}