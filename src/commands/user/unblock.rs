use sqlx::Row;
use stblib::colors::{BOLD, C_RESET, RED, LIGHT_GREEN, GRAY, YELLOW};

use crate::system_core::commands;
use crate::system_core::commands::CommandCategory;
use crate::system_core::internals::MessageToClient;
use crate::system_core::permissions::Permissions;
use crate::database::db::DATABASE;

pub fn unblock() -> commands::Command {
    async fn logic(ctx: &commands::Context) -> commands::CommandResponse {
        let user = ctx.args[0].as_str();

        let mut blocked_users: String = sqlx::query("SELECT blocked FROM users WHERE username = ?")
            .bind(&ctx.executor.username)
            .fetch_one(&DATABASE.connection)
            .await.unwrap().get("blocked");

        if blocked_users.is_empty() {
            return Ok(Some(format!("{BOLD}{YELLOW}You have not yet blocked a user{C_RESET}")))
        }

        blocked_users = blocked_users.replace(format!("{user},").as_str(), "");

        match sqlx::query("UPDATE users SET blocked = ? WHERE username = ?")
            .bind(blocked_users)
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
        name: "unblock".to_string(),
        aliases: vec![],
        description: "Unblock a user".to_string(),
        category: CommandCategory::User,
        permissions: Permissions::Member,
        required_args: 1,
        handler: |ctx| Box::pin(async move {
            logic(&ctx).await
        }),
    }
}