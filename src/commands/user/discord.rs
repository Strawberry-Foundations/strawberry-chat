use sqlx::Row;
use stblib::colors::{BOLD, C_RESET, RED, LIGHT_GREEN, RESET};

use crate::database::db::DATABASE;

use crate::system_core::commands;
use crate::system_core::commands::CommandCategory;
use crate::system_core::internals::MessageToClient;
use crate::system_core::permissions::Permissions;
use crate::utilities::role_color_parser;

pub fn discord() -> commands::Command {
    async fn logic(ctx: &commands::Context) -> commands::CommandResponse {
        if ctx.args.is_empty() {
            return (sqlx::query("SELECT discord_name FROM users WHERE username = ?")
                .bind(&ctx.executor.username)
                .fetch_one(&DATABASE.connection)
                .await).map_or_else(|_| Ok(Some(format!("{BOLD}{RED}Sorry, this user does not exist!{C_RESET}"))), |res| {
                let discord_name: String = res.get("discord_name");
                Ok(Some(format!("{BOLD}{LIGHT_GREEN}Your current Discord Name: {RESET}{discord_name}{C_RESET}")))
            });
        }


        if ctx.args[0].as_str() == "reset" || ctx.args[0].as_str() == "remove" {
            match sqlx::query("UPDATE users SET discord_name = '' WHERE username = ?")
                .bind(&ctx.executor.username)
                .execute(&DATABASE.connection)
                .await {
                Ok(..) => ..,
                Err(_) => return Ok(Some(format!("{BOLD}{RED}Sorry, this user does not exist!{C_RESET}")))
            };

            return Ok(Some(format!("{BOLD}{LIGHT_GREEN}Removed Discord Name. Rejoin to apply changes{C_RESET}")))
        }

        let discord_name = ctx.args[0..].to_vec().join(" ");

        match sqlx::query("UPDATE users SET discord_name = ? WHERE username = ?")
            .bind(&discord_name)
            .bind(&ctx.executor.username)
            .execute(&DATABASE.connection)
            .await {
            Ok(..) => ..,
            Err(_) => return Ok(Some(format!("{BOLD}{RED}Sorry, this user does not exist!{C_RESET}")))
        };

        ctx.tx_channel.send(MessageToClient::SystemMessage {
            content: format!(
                "{BOLD}{LIGHT_GREEN}Changed Discord Name to {}{discord_name}{C_RESET}{BOLD}{LIGHT_GREEN}. \
                Rejoin to apply changes{C_RESET}",
                role_color_parser(&ctx.executor.role_color)
            )
        }).await.unwrap();

        Ok(None)
    }

    commands::Command {
        name: "discord".to_string(),
        aliases: vec![],
        description: "Set your discord username".to_string(),
        category: CommandCategory::User,
        permissions: Permissions::Member,
        handler: |ctx| Box::pin(async move {
            logic(&ctx).await
        }),
    }
}