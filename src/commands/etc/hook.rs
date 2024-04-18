use tokio::spawn;

use crate::system_core::commands;
use crate::system_core::commands::CommandCategory;
use crate::system_core::hooks::Hook;
use crate::system_core::internals::MessageToClient;
use crate::system_core::permissions::Permissions;

pub fn hook() -> commands::Command {
    async fn logic(ctx: &commands::Context) -> commands::CommandResponse {
        ctx.tx_channel.send(MessageToClient::SystemMessage {
            content: "Say something!".to_string(),
        }).await.unwrap();

        let mut hook = Hook::new(ctx.executor.clone(), ctx.tx_channel.clone(), 1).await;

        spawn(async move {
            if let Some(e) = hook.rx.recv().await {
                hook.tx_ctx.send(MessageToClient::SystemMessage {
                    content: format!("Event: {e:?}")
                }).await.unwrap();
            }
        });

        Ok(None)
    }

    commands::Command {
        name: "hook".to_string(),
        aliases: vec![],
        description: "Creates a hook and prints the next event - DEBUG ONLY".to_string(),
        category: CommandCategory::Etc,
        permissions: Permissions::Member,
        handler: |ctx| Box::pin(async move {
            logic(&ctx).await
        }),
    }
}