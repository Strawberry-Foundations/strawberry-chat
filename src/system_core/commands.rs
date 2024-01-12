//! # Command System for Strawberry Chat (Rusty Edition)
//! The Strawberry Chat (Rusty Edition) command system is complex and large.
//! It includes a context-based parameter system. With this system, commands still have to be registered manually.
//! A simple context-based command can look like this:
//! ```
//! fn hello_command() -> Command {
//!     fn logic(_: Context) -> Result<Option<String>, String> {
//!         Ok(Some("Hello, World!".to_string()))
//!     }
//!
//!     Command {
//!         name: "hello".to_string(),
//!         description: "prints 'Hello, World'".to_string(),
//!         handler: |ctx| Box::pin(async move {
//!             logic(ctx)
//!         }),
//!     }
//! }
//! ```

#![allow(clippy::unnecessary_wraps)]


use tokio::sync::mpsc::Sender;
use owo_colors::OwoColorize;

use crate::system_core::message::MessageToClient;
use crate::system_core::server_core::Connection;
use crate::system_core::objects::User;

// 'static borrow from https://github.com/serenity-rs/poise/blob/c5a4fc862e22166c8933e7e11727c577bb93067d/src/lib.rs#L439
pub type BoxFuture<T> = std::pin::Pin<Box<dyn std::future::Future<Output = T> + Send>>;

#[derive(Hash, PartialEq, Eq)]
/// # Command struct
/// The command struct is the basic part for programming a command.
/// It contains information such as the name, the description and the logic (the function) of the command.
pub struct Command {
    /// Name of command (execution name, e.g. test -> /test)
    pub name: String,

    /// Description of command
    pub description: String,

    /// Logic of command (function)
    pub handler: fn(Context) -> BoxFuture<Result<Option<String>, String>>
}

/// # Context struct
/// The context struct contains all context-related information that the command requires for execution.
/// This includes user information such as user name, badge, ... and the arguments that the user has specified.
pub struct Context {
    /// The user who executed the command
    pub executor: User,

    /// Arguments that the executor passed
    pub args: Vec<String>,

    /// Target channel of user
    pub tx_channel: Sender<MessageToClient>
}


fn get_commands() -> Vec<Command> {
    let cmds = vec![
        hello_command(),
        crate::commands::etc::test_command::example_command(),
    ];

    cmds
}

pub async fn run_command(name: String, args: Vec<String>, conn: &Connection) {
    let res = exec_command(name, args, conn).await;
    match res {
        Ok(Some(text)) => conn.tx.send(
            MessageToClient::SystemMessage {
                content: text
            }
        ).await.unwrap(),
        Ok(None) => {},
        Err(e) => conn.tx.send(
            MessageToClient::SystemMessage {
                content: format!("Error running command: {e}").red().to_string()
            }
        ).await.unwrap()
    };
}

async fn exec_command(name: String, args: Vec<String>, conn: &Connection) -> Result<Option<String>, String> {
    let Some(cmd) = get_commands().into_iter().find(|cmd| cmd.name == name) else {
        return Err(String::from("Command not found"))
    };

    let Some(user) = conn.get_user() else {
        return Err(String::from("You need to authorize to run commands!"))
    };

    (cmd.handler)(
        Context {
            executor: user,
            args,
            tx_channel: conn.tx.clone()

        }
    ).await
}

fn hello_command() -> Command {
    fn logic(_: Context) -> Result<Option<String>, String> {
        Ok(Some("Hello, World!".to_string()))
    }

    Command {
        name: "hello".to_string(),
        description: "prints 'Hello, World'".to_string(),
        handler: |ctx| Box::pin(async move {
            logic(ctx)
        }),
    }
}