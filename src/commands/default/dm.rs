use sqlx::Row;

use stblib::colors::{BOLD, C_RESET, GRAY, RED, YELLOW};
use stblib::utilities::escape_ansi;

use crate::system_core::commands;
use crate::system_core::commands::CommandCategory;
use crate::system_core::internals::MessageToClient;
use crate::system_core::permissions::Permissions;
use crate::system_core::server_core::{get_senders_by_username_ignore_case, STATUS};
use crate::database::db::DATABASE;
use crate::global::LOGGER;
use crate::system_core::status::Status;
use crate::utilities::role_color_parser;

pub fn dm_basic() -> commands::Command {
    async fn logic(ctx: &commands::Context) -> commands::CommandResponse {
        let conn = get_senders_by_username_ignore_case(ctx.args[0].as_str()).await;

        if conn.is_empty() {
            return Ok(Some(format!("{BOLD}{RED}User not found or offline{C_RESET}")))
        }

        if ctx.executor.username == ctx.args[0].as_str() {
            return Ok(Some(format!("{BOLD}{YELLOW}You cannot send yourself a message!{C_RESET}")))
        }

        let data = sqlx::query("SELECT * FROM users WHERE username = ?")
            .bind(ctx.args[0].as_str())
            .fetch_all(&DATABASE.connection)
            .await.expect("err");

        let enable_dms: bool = data.first().unwrap().get("enable_dms");

        if !enable_dms {
            return Ok(Some(format!("{BOLD}{YELLOW}This user has deactivated his/her DMs{C_RESET}")))
        }

        let role_color: String = role_color_parser(data.first().unwrap().get("role_color"));
        let message: Vec<String> = ctx.args[1..].to_vec();

        ctx.tx_channel.send(MessageToClient::SystemMessage {
            content: format!(
                "{}You{C_RESET}{GRAY} --> {role_color}{}{C_RESET}: {}",
                ctx.executor.role_color,
                ctx.args[0],
                message.join(" ")
            )
        }).await.unwrap();
        
        for tx in conn {
            
            
            tx.send(MessageToClient::SystemMessage {
                content: format!(
                    "{}{}{C_RESET}{GRAY} --> {role_color}You{C_RESET}: {}",
                    ctx.executor.role_color,
                    ctx.executor.username,
                    message.join(" ")
                )
            }).await.unwrap();
            
            let status = *STATUS.read().await.get_by_name(ctx.args[0].as_str());
            if status != Status::DoNotDisturb {
                tx.send(MessageToClient::Notification {
                    title: String::from("Strawberry Chat (Direct Message)"),
                    username: format!("@{}", ctx.executor.username.clone()),
                    avatar_url: ctx.executor.avatar_url.clone(),
                    content: escape_ansi(&message.join(" ")),
                    bell: false,
                }).await.unwrap_or_else(|e| {
                    LOGGER.error(format!("Failed to send internal packet: {e}"));
                });
            }
        }

        Ok(None)
    }

    commands::Command {
        name: "dm".to_string(),
        aliases: vec![],
        description: "Send direct messages to a user".to_string(),
        category: CommandCategory::Default,
        permissions: Permissions::Member,
        required_args: 2,
        handler: |ctx| Box::pin(async move {
            logic(&ctx).await
        }),
    }
}