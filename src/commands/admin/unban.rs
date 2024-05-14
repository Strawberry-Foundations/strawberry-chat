use sqlx::Row;
use stblib::colors::{BOLD, C_RESET, RED, LIGHT_GREEN};

use crate::database::db::DATABASE;
use crate::global::LOGGER;

use crate::system_core::commands;
use crate::system_core::commands::CommandCategory;
use crate::system_core::internals::MessageToClient;
use crate::system_core::permissions::Permissions;

pub fn unban() -> commands::Command {
    async fn logic(ctx: &commands::Context) -> commands::CommandResponse {
        if ctx.args.is_empty() {
            return Ok(Some(
                format!(
                    "{BOLD}{RED}Command requires 1 argument - but only {} were given{C_RESET}",
                    ctx.args.len()
                )))
        }

        let data = sqlx::query("SELECT username, account_enabled FROM users WHERE username = ?")
            .bind(ctx.args[0].as_str())
            .fetch_all(&DATABASE.connection)
            .await.expect("err");

        if data.is_empty() {
            return Ok(Some(format!("{BOLD}{RED}Sorry, this user does not exist!{C_RESET}")))
        }

        let account_enabled: bool = data.first().unwrap().get("account_enabled");

        if account_enabled {
            return Ok(Some(format!("{BOLD}{RED}User not banned{C_RESET}")))
        }

        match sqlx::query("UPDATE users SET account_enabled = '1' WHERE username = ?")
            .bind(ctx.args[0].as_str())
            .execute(&DATABASE.connection)
            .await {
            Ok(..) => ..,
            Err(_) => return Ok(Some(format!("{BOLD}{RED}Sorry, this user does not exist!{C_RESET}")))
        };

        ctx.tx_channel.send(MessageToClient::SystemMessage {
            content: format!("{BOLD}{LIGHT_GREEN}Unbanned {}{C_RESET}", ctx.args[0])
        }).await.unwrap();

        LOGGER.info(format!("{} has been unbanned by {}", ctx.args[0], ctx.executor.username));
        Ok(None)
    }

    commands::Command {
        name: "unban".to_string(),
        aliases: vec![],
        description: "Unbans a user".to_string(),
        category: CommandCategory::Admin,
        permissions: Permissions::Admin,
        required_args: 1,
        handler: |ctx| Box::pin(async move {
            logic(&ctx).await
        }),
    }
}