use std::time::Duration;
use tokio::time::sleep;

use crate::system_core::commands;
use crate::system_core::commands::CommandCategory;
use crate::system_core::permissions::Permissions;

pub fn hang_command() -> commands::Command {
    async fn logic(_: &commands::Context) -> commands::CommandResponse {
        sleep(Duration::from_secs(20)).await;
        Ok(None)
    }

    commands::Command {
        name: "hang".to_string(),
        aliases: vec![],
        description: "Hangs the server - DEBUG ONLY".to_string(),
        category: CommandCategory::Etc,
        permissions: Permissions::Admin,
        required_args: 0,
        handler: |ctx| Box::pin(async move {
            logic(&ctx).await
        }),
    }
}