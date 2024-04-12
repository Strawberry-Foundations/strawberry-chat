use stblib::colors::{BOLD, C_RESET, RED};
use crate::constants::messages::USER_SETTINGS_HELP;

use crate::system_core::commands;
use crate::system_core::commands::CommandCategory;
use crate::system_core::internals::MessageToClient;
use crate::system_core::permissions::Permissions;

pub fn user_settings() -> commands::Command {
    async fn logic(ctx: &commands::Context) -> commands::CommandResponse {
        if ctx.args.is_empty() {
            ctx.tx_channel.send(MessageToClient::SystemMessage {
                content: format!("{RED}{BOLD}Missing arguments - Command requires at least 1 argument - Got 0 arguments{C_RESET}")
            }).await.unwrap();
        }
        
        match ctx.args[0].as_str() {
            "help" => ctx.tx_channel.send(
                    MessageToClient::SystemMessage { content: USER_SETTINGS_HELP.to_string() })
                    .await.unwrap(),
            _ => todo!(),
        }

        Ok(None)
    }

    commands::Command {
        name: "settings".to_string(),
        aliases: vec![],
        description: "Change some settings of your account".to_string(),
        category: CommandCategory::User,
        permissions: Permissions::Member,
        handler: |ctx| Box::pin(async move {
            logic(&ctx).await
        }),
    }
}