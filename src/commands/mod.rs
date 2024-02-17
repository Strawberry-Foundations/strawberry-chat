#![allow(clippy::unnecessary_wraps)]

use std::env::var;
use crate::system_core::commands::Command;

pub mod default {
    pub mod server_info;
    pub mod about;
    pub mod help;
}

pub mod user {
    pub mod online;
}

pub mod etc {
    pub mod test_command;
    pub mod hang;
    pub mod panic;
}

pub fn command_registry() -> Vec<Command> {
    let mut cmds = vec![
        default::help::help(),
        default::about::about(),
        default::server_info::server_info(),
        etc::test_command::example_command(),
        user::online::online()
    ];

    if var("DEBUG").is_ok() {
        cmds.push(etc::hang::hang_command());
        cmds.push(etc::panic::panic_command());
    }
    cmds
}