use crate::system_core::commands;
use crate::system_core::commands::CommandCategory;
use crate::system_core::internals::MessageToClient;
use crate::system_core::permissions::Permissions;

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
        permissions: Permissions::Member,
        required_args: 1,
        handler: |ctx| Box::pin(async move {
            logic(&ctx).await
        }),
    }
}