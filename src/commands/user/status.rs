use crate::system_core::commands;
use crate::system_core::commands::CommandCategory;
use crate::system_core::permissions::Permissions;
use crate::system_core::server_core::STATUS;
use crate::system_core::status::Status;

pub fn status() -> commands::Command {
    async fn logic(ctx: &commands::Context) -> commands::CommandResponse {
        STATUS.write().await.append(ctx.executor.username.as_str(), Status::Afk);

        Ok(None)
    }

    commands::Command {
        name: "status".to_string(),
        aliases: vec![],
        description: "Show or change your status".to_string(),
        category: CommandCategory::User,
        permissions: Permissions::Member,
        handler: |ctx| Box::pin(async move {
            logic(&ctx).await
        }),
    }
}