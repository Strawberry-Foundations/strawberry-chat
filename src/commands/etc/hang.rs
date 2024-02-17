use std::time::Duration;
use tokio::time::sleep;
use crate::system_core::commands;
use crate::system_core::commands::CommandCategory;
use crate::system_core::message::MessageToClient;

pub fn hang_command() -> commands::Command {
    async fn logic(ctx: &commands::Context) -> commands::CommandResponse {
        sleep(Duration::from_secs(20)).await;
        Ok(None)
    }

    commands::Command {
        name: "hang".to_string(),
        aliases: vec![],
        description: "Hangs the server - DEBUG ONLY".to_string(),
        category: CommandCategory::Etc,
        handler: |ctx| Box::pin(async move {
            logic(&ctx).await
        }),
    }
}