use sqlx::Row;
use stblib::colors::{BOLD, C_RESET, RED, LIGHT_GREEN, RESET};

use crate::system_core::commands;
use crate::system_core::commands::CommandCategory;
use crate::system_core::internals::MessageToClient;
use crate::system_core::permissions::Permissions;
use crate::utilities::role_color_parser;
use crate::database::db::DATABASE;

pub fn strawberry_id() -> commands::Command {
    async fn logic(ctx: &commands::Context) -> commands::CommandResponse {
        if ctx.args.is_empty() {
            return (sqlx::query("SELECT strawberry_id FROM users WHERE username = ?")
                .bind(&ctx.executor.username)
                .fetch_one(&DATABASE.connection)
                .await).map_or_else(|_| Ok(Some(format!("{BOLD}{RED}Sorry, this user does not exist!{C_RESET}"))), |res| {
                let strawberry_id: String = res.get("strawberry_id");
                Ok(Some(format!("{BOLD}{LIGHT_GREEN}Your current Strawberry ID: {RESET}{strawberry_id}{C_RESET}")))
            });
        }


        if ctx.args[0].as_str() == "reset" || ctx.args[0].as_str() == "remove" {
            match sqlx::query("UPDATE users SET strawberry_id = '' WHERE username = ?")
                .bind(&ctx.executor.username)
                .execute(&DATABASE.connection)
                .await {
                Ok(..) => ..,
                Err(_) => return Ok(Some(format!("{BOLD}{RED}Sorry, this user does not exist!{C_RESET}")))
            };

            return Ok(Some(format!("{BOLD}{LIGHT_GREEN}Removed Strawberry ID. Rejoin to apply changes{C_RESET}")))
        }

        let strawberry_id = ctx.args[0..].to_vec().join(" ");

        match sqlx::query("UPDATE users SET strawberry_id = ? WHERE username = ?")
            .bind(&strawberry_id)
            .bind(&ctx.executor.username)
            .execute(&DATABASE.connection)
            .await {
            Ok(..) => ..,
            Err(_) => return Ok(Some(format!("{BOLD}{RED}Sorry, this user does not exist!{C_RESET}")))
        };

        ctx.tx_channel.send(MessageToClient::SystemMessage {
            content: format!(
                "{BOLD}{LIGHT_GREEN}Changed Strawberry ID to {}{strawberry_id}{C_RESET}{BOLD}{LIGHT_GREEN}. \
                Rejoin to apply changes{C_RESET}",
                role_color_parser(&ctx.executor.role_color)
            )
        }).await.unwrap();

        Ok(None)
    }

    commands::Command {
        name: "strawberry-id".to_string(),
        aliases: vec![],
        description: "Set your Strawberry ID".to_string(),
        category: CommandCategory::User,
        permissions: Permissions::Member,
        required_args: 0,
        handler: |ctx| Box::pin(async move {
            logic(&ctx).await
        }),
    }
}