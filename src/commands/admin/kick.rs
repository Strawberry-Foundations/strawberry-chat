use stblib::colors::{BOLD, C_RESET, GREEN, RED, YELLOW};
use crate::global::LOGGER;
use crate::system_core::commands;
use crate::system_core::commands::CommandCategory;
use crate::system_core::internals::MessageToClient;
use crate::system_core::permissions::Permissions;
use crate::system_core::server_core::get_senders_by_username_ignore_case;

pub fn kick() -> commands::Command {
    async fn logic(ctx: &commands::Context) -> commands::CommandResponse {
        let user = ctx.args[0].as_str();
        let conn = get_senders_by_username_ignore_case(user).await;

        if conn.is_empty() {
            return Err(format!("{BOLD}{RED}User not found or offline{C_RESET}"))
        }

        if ctx.executor.username.to_lowercase() == ctx.args[0].as_str().to_lowercase() {
            return Err(format!("{BOLD}{YELLOW}You cannot kick yourself!{C_RESET}"))
        }

        let reason_vec: Vec<String> = ctx.args[1..].to_vec();
        let reason = if reason_vec.is_empty() {
            String::from("Not specified")
        }
        else {
            reason_vec.join(" ")
        };

        ctx.tx_channel.send(MessageToClient::SystemMessage {
            content: format!(
                "{GREEN}Kicked {user}. Reason: {reason}{C_RESET}"
            )
        }).await.unwrap();

        for tx in conn {
            tx.send(MessageToClient::SystemMessage {
                content: format!(
                    "{YELLOW}{BOLD}You got kicked from the server. Reason: {reason}{C_RESET}"
                )
            }).await.unwrap();

            tx.send(MessageToClient::Shutdown).await.unwrap();
        }

        LOGGER.info(format!("{} has been kicked by {}", user, ctx.executor.username));
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