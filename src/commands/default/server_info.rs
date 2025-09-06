use libstrawberry::colors::{BOLD, C_RESET, WHITE};

use crate::system_core::commands;
use crate::system_core::commands::CommandCategory;
use crate::system_core::internals::MessageToClient;
use crate::system_core::permissions::Permissions;
use crate::global::CONFIG;

pub fn server_info() -> commands::Command {
    async fn logic(ctx: &commands::Context) -> commands::CommandResponse {
        ctx.tx_channel.send(MessageToClient::SystemMessage {
            content: format!("{WHITE}{BOLD}{}{C_RESET}", CONFIG.server.description)
        }).await.unwrap();

        Ok(None)
    }

    commands::Command {
        name: "serverinfo".to_string(),
        aliases: vec!["server-info", "info"],
        description: "Show information about this server".to_string(),
        category: CommandCategory::Default,
        permissions: Permissions::Member,
        required_args: 0,
        handler: |ctx| Box::pin(async move {
            logic(&ctx).await
        }),
    }
}