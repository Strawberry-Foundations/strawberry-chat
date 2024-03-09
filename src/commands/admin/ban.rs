use sqlx::Row;
use stblib::colors::{BOLD, C_RESET, RED, LIGHT_GREEN, YELLOW};

use crate::database::db::DATABASE;
use crate::global::LOGGER;

use crate::system_core::commands;
use crate::system_core::commands::CommandCategory;
use crate::system_core::message::MessageToClient;
use crate::system_core::permissions::Permissions;

pub fn ban() -> commands::Command {
    async fn logic(ctx: &commands::Context) -> commands::CommandResponse {
        if ctx.args.is_empty() {
            return Ok(Some(
                format!(
                    "{BOLD}{RED}Command requires 1 argument - but only {} were given{C_RESET}",
                    ctx.args.len()
                )))
        }

        if ctx.executor.username == ctx.args[0].as_str() {
            return Ok(Some(format!("{BOLD}{YELLOW}You cannot ban yourself!{C_RESET}")))
        }

        let data = sqlx::query("SELECT username, account_enabled FROM users WHERE username = ?")
            .bind(ctx.args[0].as_str())
            .fetch_all(&DATABASE.connection)
            .await.expect("err");

        if data.is_empty() {
            return Ok(Some(format!("{BOLD}{RED}Sorry, this user does not exist!{C_RESET}")))
        }

        let account_enabled: bool = data.first().unwrap().get("account_enabled");

        if !account_enabled {
            return Ok(Some(format!("{BOLD}{RED}User already banned{C_RESET}")))
        }

        match sqlx::query("UPDATE users SET account_enabled = '0' WHERE username = ?")
            .bind(ctx.args[0].as_str())
            .execute(&DATABASE.connection)
            .await {
            Ok(..) => ..,
            Err(_) => return Ok(Some(format!("{BOLD}{RED}Sorry, this user does not exist!{C_RESET}")))
        };

        ctx.tx_channel.send(MessageToClient::SystemMessage {
            content: format!("{BOLD}{LIGHT_GREEN}Banned {}{C_RESET}", ctx.args[0])
        }).await.unwrap();

        LOGGER.info(format!("{} has been banned by {}", ctx.args[0], ctx.executor.username));
        Ok(None)
    }

    commands::Command {
        name: "ban".to_string(),
        aliases: vec![],
        description: "Bans a user".to_string(),
        category: CommandCategory::Admin,
        permissions: Permissions::Admin,
        handler: |ctx| Box::pin(async move {
            logic(&ctx).await
        }),
    }
}