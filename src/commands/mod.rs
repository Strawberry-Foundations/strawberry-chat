#![allow(clippy::unnecessary_wraps)]

use std::env::var;
use crate::system_core::commands::Command;

pub mod default {
    pub mod server_info;
    pub mod about;
    pub mod help;
    pub mod dm;
}

pub mod user {
    pub mod online;
    pub mod members;
    pub mod nickname;
    pub mod description;
    pub mod userinfo;
    pub mod user_settings;
    pub mod strawberry_id;
    pub mod memberlist;
    pub mod badge;
    pub mod status;
    pub mod block;
    pub mod unblock;
}

pub mod etc {
    pub mod test_command;
    pub mod hang;
    pub mod panic;
    pub mod hook;
    pub mod delete_account;
}

pub mod admin {
    pub mod ban;
    pub mod unban;
    pub mod mute;
    pub mod unmute;
    pub mod broadcast;
    pub mod admin_settings;
}

pub fn command_registry() -> Vec<Command> {
    let mut cmds = vec![
        default::help::help(),
        default::about::about(),
        default::dm::dm_basic(),
        default::server_info::server_info(),
        
        user::online::online(),
        user::status::status(),
        user::members::members(),
        user::memberlist::memberlist(),
        user::nickname::nickname(),
        user::description::description(),
        user::userinfo::userinfo(),
        user::user_settings::user_settings(),
        user::strawberry_id::strawberry_id(),
        user::badge::badge(),
        user::block::block(),
        user::unblock::unblock(),
        
        admin::broadcast::broadcast(),
        admin::ban::ban(),
        admin::unban::unban(),
        admin::mute::mute(),
        admin::unmute::unmute(),
        admin::admin_settings::admin_settings(),

        etc::test_command::example_command(),
        etc::delete_account::delete_account(),
    ];

    if var("DEBUG").is_ok() {
        cmds.push(etc::hang::hang_command());
        cmds.push(etc::panic::panic_command());
        cmds.push(etc::hook::hook());
    }
    cmds
}