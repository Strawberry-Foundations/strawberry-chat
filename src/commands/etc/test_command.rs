use crate::system_core::commands;
use crate::system_core::message::MessageToClient;

pub fn example_command() -> commands::Command {
    async fn logic(ctx: &commands::Context) -> Result<Option<String>, String> {
        ctx.tx_channel.send(MessageToClient::SystemMessage { content: format!("Username: {}", ctx.executor.username) }).await.unwrap();
        ctx.tx_channel.send(MessageToClient::SystemMessage { content: format!("Args: {:?}", ctx.args) }).await.unwrap();
        Ok(None)
    }

    commands::Command {
        name: "test".to_string(),
        description: "Example command".to_string(),
        handler: |ctx| Box::pin(async move {
            logic(&ctx).await
        }),
    }
}