use tokio::spawn;
use tokio::sync::mpsc::channel;
use crate::system_core::commands;
use crate::system_core::commands::CommandCategory;
use crate::system_core::internals::MessageToClient;
use crate::system_core::permissions::Permissions;
use crate::system_core::server_core::{Event, register_hook};

pub fn hook() -> commands::Command {
    async fn logic(ctx: &commands::Context) -> commands::CommandResponse {
        ctx.tx_channel.send(MessageToClient::SystemMessage {
            content: "Say something!".to_string(),
        }).await.unwrap();
        
        let (tx, mut rx) = channel::<Event>(32);
        register_hook(tx, ctx.executor.clone()).await;
        let tx = ctx.tx_channel.clone();
        spawn(async move {
            if let Some(e) = rx.recv().await {
                tx.send(MessageToClient::SystemMessage {
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