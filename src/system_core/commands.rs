//! # Command System for Strawberry Chat (Rusty Edition)
//! The Strawberry Chat (Rusty Edition) command system is complex and large.
//! It includes a context-based parameter system. With this system, commands still have to be registered manually.
//! A simple context-based command can look like this:
//! ```
//! fn hello_command() -> Command {
//!     fn logic(_: Context) -> CommandResponse {
//!         Ok(Some("Hello, World!".to_string()))
//!     }
//!
//!    Command {
//!         name: "hello".to_string(),
//!         aliases: vec![],
//!         description: "prints 'Hello, World'".to_string(),
//!         category: CommandCategory::Etc,
//!         permissions: Permissions::Member,
//!         required_args: 0,
//!         handler: |ctx| Box::pin(async move {
//!             logic(ctx)
//!         }),
//!     }
//! }
//! ```

#![allow(clippy::unnecessary_wraps)]

use tokio::sync::mpsc::Sender;
use owo_colors::OwoColorize;
use sqlx::Row;

use stblib::stbchat::object::User;
use stblib::colors::{BOLD, C_RESET, RED};

use crate::system_core::internals::MessageToClient;
use crate::system_core::permissions::Permissions;
use crate::system_core::server_core::Connection;
use crate::commands::command_registry;
use crate::database::DATABASE;


// 'static borrow from https://github.com/serenity-rs/poise/blob/c5a4fc862e22166c8933e7e11727c577bb93067d/src/lib.rs#L439
pub type BoxFuture<T> = std::pin::Pin<Box<dyn std::future::Future<Output = T> + Send>>;
pub type CommandResponse = Result<Option<String>, String>;

/// # Command struct
/// The command struct is the basic part for programming a command.
/// It contains information such as the name, the description and the logic (the function) of the command.
#[derive(Hash, PartialEq, Eq)]
pub struct Command {
    /// Name of command (execution name, e.g. test -> /test)
    pub name: String,

    /// Aliases for commands
    pub aliases: Vec<&'static str>,

    /// Description of command
    pub description: String,
    
    /// Category of command
    pub category: CommandCategory,

    /// Required permissions
    pub permissions: Permissions,

    /// Required count of args
    pub required_args: usize,
    
    /// Logic of command (function)
    pub handler: fn(Context) -> BoxFuture<CommandResponse>,
}

/// # Context struct
/// The context struct contains all context-related information that the command requires for execution.
/// This includes user information such as username, badge, ... and the arguments that the user has specified.
#[derive(Clone)]
pub struct Context {
    /// The user who executed the command
    pub executor: User,

    /// Arguments that the executor passed
    pub args: Vec<String>,

    /// Target channel of user
    pub tx_channel: Sender<MessageToClient>
}

#[derive(Hash, PartialEq, Eq)]
pub enum CommandCategory {
    Default,
    Etc,
    General,
    User,
    System,
    Admin
}

pub fn get_commands_category(command_category: &CommandCategory) -> Vec<Command> {
    command_registry()
        .into_iter()
        .filter(|cmd| cmd.category == *command_category)
        .collect()
}


pub async fn run_command(name: String, args: Vec<String>, conn: &Connection) {
    let res = exec_command(name, args, conn).await;
    
    match res {
        Ok(Some(message)) => conn.tx.send(
            MessageToClient::SystemMessage { content: format!("{message}{C_RESET}") }
        ).await.unwrap(),
        Ok(None) => {},
        Err(e) => conn.tx.send(
            MessageToClient::SystemMessage { content: e.to_string().red().to_string() }
        ).await.unwrap()
    };
}

async fn exec_command(name: String, args: Vec<String>, conn: &Connection) -> Result<Option<String>, String> {
    let Some(cmd) = command_registry()
        .into_iter()
        .find(|cmd| cmd.name == name || cmd.aliases.contains(&name.as_str())) else {
        return Err(format!("Command '{name}' not found"))
    };

    let Some(user) = conn.get_user() else {
        return Err(String::from("You need to authorize to run commands!"))
    };

    let data = sqlx::query("SELECT role FROM users WHERE username = ?")
        .bind(user.username.clone())
        .fetch_all(&DATABASE.connection)
        .await.expect("err");

    if data.is_empty() {
        return Err(format!("{BOLD}{RED}Sorry, this user does not exist!{C_RESET}"))
    }

    let user_permissions = match data.first().unwrap().get("role") {
        "bot" => Permissions::Bot,
        "admin" => Permissions::Admin,
        _ => Permissions::Member,
    };
    
    if (cmd.permissions) == Permissions::Admin && user_permissions == Permissions::Member {
        return Err(String::from("You do not have permissions to run this command!"))
    }

    if args.len() < (cmd.required_args) {
        return Err(format!(
            "Missing arguments - Command requires at least {} argument - Got {} arguments",
            (cmd.required_args), args.len()
        ))
    }

    (cmd.handler)(
        Context {
            executor: user,
            args,
            tx_channel: conn.tx.clone()

        }
    ).await
}

fn hello_command() -> Command {
    fn logic(_: Context) -> CommandResponse {
        Ok(Some("Hello, World!".to_string()))
    }

    Command {
        name: "hello".to_string(),
        aliases: vec![],
        description: "prints 'Hello, World'".to_string(),
        category: CommandCategory::Etc,
        permissions: Permissions::Member,
        required_args: 0,
        handler: |ctx| Box::pin(async move {
            logic(ctx)
        }),
    }
}