use stblib::colors::{BOLD, C_RESET, RED, LIGHT_GREEN};

use crate::system_core::commands;
use crate::system_core::commands::CommandCategory;
use crate::system_core::internals::MessageToClient;
use crate::system_core::permissions::Permissions;
use crate::database::DATABASE;
use crate::global::LOGGER;

pub fn unmute() -> commands::Command {
    async fn logic(ctx: &commands::Context) -> commands::CommandResponse {
        let muted = DATABASE.is_user_muted(ctx.args[0].as_str()).await;

        if muted.is_none() {
            return Err(format!("{BOLD}{RED}Sorry, this user does not exist!{C_RESET}"))
        }

        if !muted.unwrap() {
            return Err(format!("{BOLD}{RED}User already muted{C_RESET}"))
        }

        DATABASE.update_val(ctx.args[0].as_str(),"muted", "0").await.unwrap();

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