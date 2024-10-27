use sqlx::Row;
use stblib::colors::{BOLD, C_RESET, RED, LIGHT_GREEN, RESET};

use crate::system_core::commands;
use crate::system_core::commands::CommandCategory;
use crate::system_core::internals::MessageToClient;
use crate::system_core::permissions::Permissions;
use crate::utilities::role_color_parser;
use crate::database::DATABASE;

pub fn description() -> commands::Command {
    async fn logic(ctx: &commands::Context) -> commands::CommandResponse {
        if ctx.args.is_empty() { 
            return (sqlx::query("SELECT description FROM users WHERE username = ?")
                .bind(&ctx.executor.username)
                .fetch_one(&DATABASE.connection)
                .await).map_or_else(|_| Err(format!("{BOLD}{RED}Sorry, this user does not exist!{C_RESET}")), |res| {
                    let description: String = res.get("description");
                    Ok(Some(format!("{BOLD}{LIGHT_GREEN}Your current description: {RESET}{description}{C_RESET}")))
                });
        }


        if ctx.args[0].as_str() == "reset" || ctx.args[0].as_str() == "remove" {
            DATABASE.update_description(&ctx.executor.username, "").await;

            return Ok(Some(format!("{BOLD}{LIGHT_GREEN}Removed description. Rejoin to apply changes{C_RESET}")))
        }

        let description = ctx.args[0..].to_vec().join(" ");

        DATABASE.update_description(&ctx.executor.username, &description).await;

        ctx.tx_channel.send(MessageToClient::SystemMessage {
            content: format!(
                "{BOLD}{LIGHT_GREEN}Changed description to {}{description}{C_RESET}{BOLD}{LIGHT_GREEN}. \
                Rejoin to apply changes{C_RESET}",
                role_color_parser(&ctx.executor.role_color)
            )
        }).await.unwrap();

        Ok(None)
    }

    commands::Command {
        name: "description".to_string(),
        aliases: vec!["desc"],
        description: "Display or change your description".to_string(),
        category: CommandCategory::User,
        permissions: Permissions::Member,
        required_args: 0,
        handler: |ctx| Box::pin(async move {
            logic(&ctx).await
        }),
    }
}