use stblib::colors::{BOLD, C_RESET, WHITE};

use crate::global::CONFIG;
use crate::system_core::commands;
use crate::system_core::commands::CommandCategory;
use crate::system_core::message::MessageToClient;

pub fn dm_basic() -> commands::Command {
    async fn logic(ctx: &commands::Context) -> commands::CommandResponse {
        ctx.tx_channel.send(MessageToClient::SystemMessage {
            content: format!("{WHITE}{BOLD}{}{C_RESET}", CONFIG.server.description)
        }).await.unwrap();

        Ok(None)
    }

    commands::Command {
        name: "dm".to_string(),
        aliases: vec![],
        description: "Send direct messages to a user".to_string(),
        category: CommandCategory::Default,
        handler: |ctx| Box::pin(async move {
            logic(&ctx).await
        }),
    }
}