use stblib::colors::{BOLD, C_RESET, RED, LIGHT_GREEN};

use crate::system_core::commands;
use crate::system_core::commands::CommandCategory;
use crate::system_core::internals::MessageToClient;
use crate::system_core::permissions::Permissions;
use crate::utilities::role_color_parser;
use crate::database::db::DATABASE;

pub fn nickname() -> commands::Command {
    async fn logic(ctx: &commands::Context) -> commands::CommandResponse {
        if ctx.args.is_empty() {
            return Ok(Some(
                format!(
                    "{BOLD}{RED}Command requires a minimum of 1 argument - but only {} were given{C_RESET}",
                    ctx.args.len()
                )))
        }


        if ctx.args[0].as_str() == "reset" || ctx.args[0].as_str() == "remove" {
            match sqlx::query("UPDATE users SET nickname = '' WHERE username = ?")
                .bind(&ctx.executor.username)
                .execute(&DATABASE.connection)
                .await {
                Ok(..) => ..,
                Err(_) => return Ok(Some(format!("{BOLD}{RED}Sorry, this user does not exist!{C_RESET}")))
            };

            return Ok(Some(format!("{BOLD}{LIGHT_GREEN}Removed nickname. Rejoin to apply changes{C_RESET}")))
        }

        let nickname = ctx.args[0..].to_vec().join(" ");

        match sqlx::query("UPDATE users SET nickname = ? WHERE username = ?")
            .bind(&nickname)
            .bind(&ctx.executor.username)
            .execute(&DATABASE.connection)
            .await {
            Ok(..) => ..,
            Err(_) => return Ok(Some(format!("{BOLD}{RED}Sorry, this user does not exist!{C_RESET}")))
        };

        ctx.tx_channel.send(MessageToClient::SystemMessage {
            content: format!(
                "{BOLD}{LIGHT_GREEN}Changed nickname to {}{nickname}{C_RESET}{BOLD}{LIGHT_GREEN}. \
                Rejoin to apply changes{C_RESET}",
                role_color_parser(&ctx.executor.role_color)
            )
        }).await.unwrap();

        Ok(None)
    }

    commands::Command {
        name: "nickname".to_string(),
        aliases: vec!["nick"],
        description: "Change your nickname".to_string(),
        category: CommandCategory::User,
        permissions: Permissions::Member,
        required_args: 1,
        handler: |ctx| Box::pin(async move {
            logic(&ctx).await
        }),
    }
}