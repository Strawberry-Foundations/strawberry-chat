use stblib::colors::{BOLD, C_RESET, RED, LIGHT_GREEN, YELLOW};

use crate::system_core::commands;
use crate::system_core::commands::CommandCategory;
use crate::system_core::internals::MessageToClient;
use crate::system_core::permissions::Permissions;
use crate::database::DATABASE;
use crate::global::LOGGER;

pub fn ban() -> commands::Command {
    async fn logic(ctx: &commands::Context) -> commands::CommandResponse {
        if ctx.executor.username == ctx.args[0].as_str() {
            return Err(format!("{BOLD}{YELLOW}You cannot ban yourself!{C_RESET}"))
        }

        let account_enabled = DATABASE.is_account_enabled(&ctx.args[0].as_str()).await;

        if account_enabled.is_none() {
            return Err(format!("{BOLD}{RED}Sorry, this user does not exist!{C_RESET}"))
        }

        if !account_enabled.unwrap() {
            return Err(format!("{BOLD}{RED}User already banned{C_RESET}"))
        }
        
        DATABASE.update_val(&ctx.args[0].as_str(),"account_enabled", "0").await;

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
        required_args: 1,
        handler: |ctx| Box::pin(async move {
            logic(&ctx).await
        }),
    }
}