#![allow(clippy::unnecessary_wraps)]

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
}

pub fn command_registry() -> Vec<Command> {
    vec![
        default::help::help(),
        default::about::about(),
        default::server_info::server_info(),
        etc::test_command::example_command(),
        user::online::online(),
    ]
}