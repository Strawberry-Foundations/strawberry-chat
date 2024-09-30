use sqlx::Row;

use stblib::colors::{BOLD, C_RESET, GRAY, GREEN, RED, YELLOW};
use stblib::utilities::escape_ansi;

use crate::system_core::commands;
use crate::system_core::commands::CommandCategory;
use crate::system_core::internals::MessageToClient;
use crate::system_core::permissions::Permissions;
use crate::system_core::server_core::{get_senders_by_username_ignore_case, STATUS};
use crate::system_core::status::Status;
use crate::database::db::DATABASE;
use crate::global::LOGGER;
use crate::utilities::role_color_parser;

pub fn kick() -> commands::Command {
    async fn logic(ctx: &commands::Context) -> commands::CommandResponse {
        let user = ctx.args[0].as_str();
        let conn = get_senders_by_username_ignore_case(user).await;

        if conn.is_empty() {
            return Err(format!("{BOLD}{RED}User not found or offline{C_RESET}"))
        }

        if ctx.executor.username == ctx.args[0].as_str() {
            return Err(format!("{BOLD}{YELLOW}You cannot kick yourself!{C_RESET}"))
        }

        let reason: Vec<String> = ctx.args[1..].to_vec();

        ctx.tx_channel.send(MessageToClient::SystemMessage {
            content: format!(
                "{GREEN}Kicked {user}. Reason: {}{C_RESET}",
                reason.join(" ")
            )
        }).await.unwrap();

        for tx in conn {
            tx.send(MessageToClient::SystemMessage {
                content: format!(
                    "{YELLOW}{BOLD}You got kicked from the server. Reason: {}{C_RESET}",
                    reason.join(" ")
                )
            }).await.unwrap();
            
            tx.send(MessageToClient::Shutdown).await.unwrap();
        }

        Ok(None)
    }

    commands::Command {
        name: "kick".to_string(),
        aliases: vec![],
        description: "Kick a user".to_string(),
        category: CommandCategory::Admin,
        permissions: Permissions::Admin,
        required_args: 1,
        handler: |ctx| Box::pin(async move {
            logic(&ctx).await
        }),
    }
}