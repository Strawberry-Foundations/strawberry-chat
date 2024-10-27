use stblib::colors::{BOLD, C_RESET, RED, LIGHT_GREEN};

use crate::system_core::commands;
use crate::system_core::commands::CommandCategory;
use crate::system_core::internals::MessageToClient;
use crate::system_core::permissions::Permissions;
use crate::database::DATABASE;
use crate::global::LOGGER;

pub fn unban() -> commands::Command {
    async fn logic(ctx: &commands::Context) -> commands::CommandResponse {
        let account_enabled = DATABASE.is_account_enabled(ctx.args[0].as_str()).await;

        if account_enabled.is_none() {
            return Err(format!("{BOLD}{RED}Sorry, this user does not exist!{C_RESET}"))
        }

        if account_enabled.unwrap() {
            return Err(format!("{BOLD}{RED}User not banned{C_RESET}"))
        }

        DATABASE.update_val(ctx.args[0].as_str(),"account_enabled", "1").await.unwrap();

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
