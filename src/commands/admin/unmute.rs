use sqlx::Row;
use stblib::colors::{BOLD, C_RESET, RED, LIGHT_GREEN};

use crate::database::db::DATABASE;
use crate::global::LOGGER;

use crate::system_core::commands;
use crate::system_core::commands::CommandCategory;
use crate::system_core::internals::MessageToClient;
use crate::system_core::permissions::Permissions;

pub fn unmute() -> commands::Command {
    async fn logic(ctx: &commands::Context) -> commands::CommandResponse {
        if ctx.args.is_empty() {
            return Ok(Some(
                format!(
                    "{BOLD}{RED}Command requires 1 argument - but only {} were given{C_RESET}",
                    ctx.args.len()
                )))
        }

        let data = sqlx::query("SELECT username, muted FROM users WHERE username = ?")
            .bind(ctx.args[0].as_str())
            .fetch_all(&DATABASE.connection)
            .await.expect("err");

        if data.is_empty() {
            return Ok(Some(format!("{BOLD}{RED}Sorry, this user does not exist!{C_RESET}")))
        }

        let muted: bool = data.first().unwrap().get("muted");

        if !muted {
            return Ok(Some(format!("{BOLD}{RED}User not muted{C_RESET}")))
        }

        match sqlx::query("UPDATE users SET muted = '0' WHERE username = ?")
            .bind(ctx.args[0].as_str())
            .execute(&DATABASE.connection)
            .await {
            Ok(..) => ..,
            Err(_) => return Ok(Some(format!("{BOLD}{RED}Sorry, this user does not exist!{C_RESET}")))
        };

        ctx.tx_channel.send(MessageToClient::SystemMessage {
            content: format!("{BOLD}{LIGHT_GREEN}Unmuted {}{C_RESET}", ctx.args[0])
        }).await.unwrap();

        LOGGER.info(format!("{} has been unmuted by {}", ctx.args[0], ctx.executor.username));
        Ok(None)
    }

    commands::Command {
        name: "unmute".to_string(),
        aliases: vec![],
        description: "Unmutes a user".to_string(),
        category: CommandCategory::Admin,
        permissions: Permissions::Admin,
        required_args: 1,
        handler: |ctx| Box::pin(async move {
            logic(&ctx).await
        }),
    }
}