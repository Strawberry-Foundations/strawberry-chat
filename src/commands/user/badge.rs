use sqlx::Row;
use stblib::colors::{BOLD, C_RESET, RED, LIGHT_GREEN, YELLOW};

use crate::system_core::commands;
use crate::system_core::commands::CommandCategory;
use crate::system_core::internals::MessageToClient;
use crate::system_core::permissions::Permissions;
use crate::utilities::role_color_parser;
use crate::database::db::DATABASE;

pub fn badge() -> commands::Command {
    async fn logic(ctx: &commands::Context) -> commands::CommandResponse {
        if ctx.args.is_empty() {
            return Ok(Some(format!("{BOLD}{YELLOW}Please provide a valid badge{C_RESET}")))
        }

        if ctx.args[0].as_str() == "reset" || ctx.args[0].as_str() == "remove" {
            match sqlx::query("UPDATE users SET badge = '' WHERE username = ?")
                .bind(&ctx.executor.username)
                .execute(&DATABASE.connection)
                .await {
                Ok(..) => ..,
                Err(_) => return Ok(Some(format!("{BOLD}{RED}Sorry, this user does not exist!{C_RESET}")))
            };

            return Ok(Some(format!("{BOLD}{LIGHT_GREEN}Removed badge. Rejoin to apply changes{C_RESET}")))
        }

        let badge = &ctx.args[0];


        let badges: String = sqlx::query("SELECT badges FROM users WHERE username = ?")
            .bind(&ctx.executor.username)
            .fetch_one(&DATABASE.connection)
            .await.unwrap().get("badges");
        
        if !badges.contains(badge) {
            return Ok(Some(format!("{BOLD}{RED}You do not own this badge!{C_RESET}")))
        }

        match sqlx::query("UPDATE users SET badge = ? WHERE username = ?")
            .bind(badge)
            .bind(&ctx.executor.username)
            .execute(&DATABASE.connection)
            .await {
            Ok(..) => ..,
            Err(_) => return Ok(Some(format!("{BOLD}{RED}Sorry, this user does not exist!{C_RESET}")))
        };

        ctx.tx_channel.send(MessageToClient::SystemMessage {
            content: format!(
                "{BOLD}{LIGHT_GREEN}Changed your main badge to {}{badge}{C_RESET}{BOLD}{LIGHT_GREEN}. \
                Rejoin to apply changes{C_RESET}",
                role_color_parser(&ctx.executor.role_color)
            )
        }).await.unwrap();

        Ok(None)
    }

    commands::Command {
        name: "badge".to_string(),
        aliases: vec![],
        description: "Set your main badge".to_string(),
        category: CommandCategory::User,
        permissions: Permissions::Member,
        handler: |ctx| Box::pin(async move {
            logic(&ctx).await
        }),
    }
}