use libstrawberry::colors::{BOLD, C_RESET, RED, LIGHT_GREEN, GRAY, CYAN, GREEN, YELLOW};

use crate::system_core::commands;
use crate::system_core::commands::CommandCategory;
use crate::system_core::internals::MessageToClient;
use crate::system_core::permissions::Permissions;
use crate::database::DATABASE;

pub fn block() -> commands::Command {
    async fn logic(ctx: &commands::Context) -> commands::CommandResponse {
        let user = ctx.args[0].as_str();

        if user == "list" {
            let blocked_users = DATABASE.get_val_from_user(&ctx.executor.username, "blocked").await.unwrap();

            if blocked_users.is_empty() {
                return Err(format!("{BOLD}{YELLOW}You have not yet blocked a user{C_RESET}"))
            }

            let blocked_users: Vec<&str> = blocked_users.split(',').collect();
            let blocked_users: String = if blocked_users.len() == 2 {
                blocked_users.join(", ").replace(',', "")
            }
            else {
                blocked_users.join(", ")
            };

            return Ok(Some(format!("{BOLD}{GREEN}Blocked users: {CYAN}{blocked_users}{C_RESET}")))
        }

        if user == ctx.executor.username {
            return Err(format!("{BOLD}{YELLOW}You cannot block yourself{C_RESET}"))
        }

        if !DATABASE.is_username_taken(user).await {
            return Err(format!("{BOLD}{RED}Sorry, this user does not exist!{C_RESET}"))
        }

        let blocked_users = DATABASE.get_val_from_user(&ctx.executor.username, "blocked").await.unwrap();
        
        if blocked_users.split(',').any(|x| x == user) {
            return Err(format!("{BOLD}{YELLOW}This user is already blocked{C_RESET}"))
        }

        let new_blocked_users: String = if blocked_users.is_empty() {
            format!("{user},")
        }
        else {
            format!("{blocked_users}{user},")
        };

        DATABASE.update_val(&ctx.executor.username, "blocked", &new_blocked_users).await.unwrap();

        ctx.tx_channel.send(MessageToClient::SystemMessage {
            content: format!("{BOLD}{LIGHT_GREEN}Blocked {user}. Type {GRAY}/unblock {user}{LIGHT_GREEN} to unblock{C_RESET}")
        }).await.unwrap();

        Ok(None)
    }

    commands::Command {
        name: "block".to_string(),
        aliases: vec![],
        description: "Block a user".to_string(),
        category: CommandCategory::User,
        permissions: Permissions::Member,
        required_args: 1,
        handler: |ctx| Box::pin(async move {
            logic(&ctx).await
        }),
    }
}