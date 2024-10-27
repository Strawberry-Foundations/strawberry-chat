use stblib::colors::{BOLD, C_RESET, RED, LIGHT_GREEN, YELLOW};

use crate::database::DATABASE;
use crate::global::LOGGER;

use crate::system_core::commands;
use crate::system_core::commands::CommandCategory;
use crate::system_core::internals::MessageToClient;
use crate::system_core::permissions::Permissions;

pub fn mute() -> commands::Command {
    async fn logic(ctx: &commands::Context) -> commands::CommandResponse {
        if ctx.executor.username == ctx.args[0].as_str() {
            return Err(format!("{BOLD}{YELLOW}You cannot mute yourself!{C_RESET}"))
        }

        let muted = DATABASE.is_user_muted(ctx.args[0].as_str()).await;

        if muted.is_none() {
            return Err(format!("{BOLD}{RED}Sorry, this user does not exist!{C_RESET}"))
        }

        if muted.unwrap() {
            return Err(format!("{BOLD}{RED}User already muted{C_RESET}"))
        }

        DATABASE.update_val(ctx.args[0].as_str(),"muted", "1").await.unwrap();

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
        required_args: 1,
        handler: |ctx| Box::pin(async move {
            logic(&ctx).await
        }),
    }
}