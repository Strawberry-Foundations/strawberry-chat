use sqlx::Row;
use stblib::colors::{BOLD, C_RESET, RED, LIGHT_GREEN, YELLOW};

use crate::database::db::DATABASE;
use crate::global::LOGGER;

use crate::system_core::commands;
use crate::system_core::commands::CommandCategory;
use crate::system_core::message::MessageToClient;
use crate::system_core::permissions::Permissions;

pub fn mute() -> commands::Command {
    async fn logic(ctx: &commands::Context) -> commands::CommandResponse {
        if ctx.args.is_empty() {
            return Ok(Some(
                format!(
                    "{BOLD}{RED}Command requires 1 argument - but only {} were given{C_RESET}",
                    ctx.args.len()
                )))
        }

        if ctx.executor.username == ctx.args[0].as_str() {
            return Ok(Some(format!("{BOLD}{YELLOW}You cannot mute yourself a message!{C_RESET}")))
        }

        let data = sqlx::query("SELECT username, muted FROM users WHERE username = ?")
            .bind(ctx.args[0].as_str())
            .fetch_all(&DATABASE.connection)
            .await.expect("err");

        if data.is_empty() {
            return Ok(Some(format!("{BOLD}{RED}Sorry, this user does not exist!{C_RESET}")))
        }

        let muted: bool = data.first().unwrap().get("muted");
        
        if muted {
            return Ok(Some(format!("{BOLD}{RED}User already muted{C_RESET}")))
        }

        match sqlx::query("UPDATE users SET muted = '1' WHERE username = ?")
            .bind(ctx.args[0].as_str())
            .execute(&DATABASE.connection)
            .await {
            Ok(..) => ..,
            Err(_) => return Ok(Some(format!("{BOLD}{RED}Sorry, this user does not exist!{C_RESET}")))
        };

        ctx.tx_channel.send(MessageToClient::SystemMessage {
            content: format!("{BOLD}{LIGHT_GREEN}Muted {}{C_RESET}", ctx.args[0])
        }).await.unwrap();

        LOGGER.info(format!("{} has been muted by {}", ctx.args[0], ctx.executor.username));
        Ok(None)
    }

    commands::Command {
        name: "mute".to_string(),
        aliases: vec![],
        description: "Mutes a user".to_string(),
        category: CommandCategory::Admin,
        permissions: Permissions::Admin,
        handler: |ctx| Box::pin(async move {
            logic(&ctx).await
        }),
    }
}