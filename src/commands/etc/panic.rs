use std::time::Duration;
use tokio::time::sleep;
use crate::system_core::commands;
use crate::system_core::commands::CommandCategory;
use crate::system_core::message::MessageToClient;

pub fn panic_command() -> commands::Command {
    async fn logic(ctx: &commands::Context) -> commands::CommandResponse {
        panic!();
        Ok(None)
    }

    commands::Command {
        name: "panic".to_string(),
        aliases: vec![],
        description: "Panicks - DEBUG ONLY".to_string(),
        category: CommandCategory::Etc,
        handler: |ctx| Box::pin(async move {
            logic(&ctx).await
        }),
    }
}