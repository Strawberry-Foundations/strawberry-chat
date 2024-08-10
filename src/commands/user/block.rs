use sqlx::Row;
use stblib::colors::{BOLD, C_RESET, RED, LIGHT_GREEN, GRAY, CYAN, GREEN};

use crate::system_core::commands;
use crate::system_core::commands::CommandCategory;
use crate::system_core::internals::MessageToClient;
use crate::system_core::permissions::Permissions;
use crate::database::db::DATABASE;

pub fn block() -> commands::Command {
    async fn logic(ctx: &commands::Context) -> commands::CommandResponse {
        let user = ctx.args[0].as_str();

        if user == "list" {
            let blocked_users: String = sqlx::query("SELECT blocked FROM users WHERE username = ?")
                .bind(&ctx.executor.username)
                .fetch_one(&DATABASE.connection)
                .await.unwrap().get("blocked");

            let blocked_users: Vec<&str> = blocked_users.split(',').collect();

            return Ok(Some(format!("{BOLD}{GREEN}Blocked users: {CYAN}{}{C_RESET}", blocked_users.join(", "))))
        }

        if !DATABASE.is_username_taken(&user.to_string()).await {
            return Ok(Some(format!("{BOLD}{RED}Sorry, this user does not exist!{C_RESET}")))
        }

        let blocked_users: String = sqlx::query("SELECT blocked FROM users WHERE username = ?")
            .bind(&ctx.executor.username)
            .fetch_one(&DATABASE.connection)
            .await.unwrap().get("blocked");

        let new_blocked_users: String = if blocked_users.is_empty() {
            format!("{user},")
        }
        else {
            format!("{blocked_users}{user},")
        };

        match sqlx::query("UPDATE users SET blocked = ? WHERE username = ?")
            .bind(new_blocked_users)
            .bind(&ctx.executor.username)
            .execute(&DATABASE.connection)
            .await {
            Ok(..) => ..,
            Err(_) => return Ok(Some(format!("{BOLD}{RED}Sorry, this user does not exist!{C_RESET}")))
        };

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