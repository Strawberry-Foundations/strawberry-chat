use std::time::Duration;
use tokio::time::sleep;
use crate::system_core::commands;
use crate::system_core::commands::CommandCategory;
use crate::system_core::message::MessageToClient;

pub fn example_command() -> commands::Command {
    async fn logic(ctx: &commands::Context) -> commands::CommandResponse {
        ctx.tx_channel.send(MessageToClient::SystemMessage { content: format!("Username: {}", ctx.executor.username) }).await.unwrap();
        ctx.tx_channel.send(MessageToClient::SystemMessage { content: format!("Args: {:?}", ctx.args) }).await.unwrap();
        Ok(None)
    }

    commands::Command {
        name: "test".to_string(),
        aliases: vec![],
        description: "Example command".to_string(),
        category: CommandCategory::Etc,
        handler: |ctx| Box::pin(async move {
            logic(&ctx).await
        }),
    }
}