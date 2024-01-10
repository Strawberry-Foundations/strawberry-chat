#![allow(clippy::unnecessary_wraps)]

use owo_colors::OwoColorize;
use crate::system_core::message::MessageToClient;
use crate::system_core::server_core::Connection;
use crate::system_core::user::UserObject;

// 'static borrow from https://github.com/serenity-rs/poise/blob/c5a4fc862e22166c8933e7e11727c577bb93067d/src/lib.rs#L439
pub type BoxFuture<T> = std::pin::Pin<Box<dyn std::future::Future<Output = T> + Send>>;

pub struct Context {
    /// The user who executed the command
    pub executor: UserObject,
    pub args: Vec<String>,
}

#[derive(Hash, PartialEq, Eq)]
pub struct Command {
    pub name: String,
    pub description: String,
    pub handler: fn(Context) -> BoxFuture<Result<String, String>>
}

fn get_commands() -> Vec<Command> {
    let mut cmds = vec![
        hello_command()
    ];

    cmds
}

pub async fn run_command(name: String, args: Vec<String>, conn: &mut Connection) {
    let res = exec_command(name, args, conn).await;
    match res {
        Ok(text) => conn.tx.send(
            MessageToClient::SystemMessage {
                content: text
            }
        ).unwrap(),

        Err(e) => conn.tx.send(
            MessageToClient::SystemMessage {
                content: format!("Error running command: {e}").red().to_string()
            }
        ).unwrap()
    };
}

async fn exec_command(name: String, args: Vec<String>, conn: &mut Connection) -> Result<String, String> {
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
        }
    ).await
}

fn hello_command() -> Command {
    fn logic(_: Context) -> Result<String, String> {
        Ok("Hello, World!".to_string())
    }

    Command {
        name: "hello".to_string(),
        description: "prints 'Hello, World'".to_string(),
        handler: |ctx| Box::pin(async move {
            logic(ctx)
        }),
    }
}