use libstrawberry::colors::{BOLD, C_RESET, LIGHT_GREEN, YELLOW};

use crate::system_core::commands;
use crate::system_core::commands::CommandCategory;
use crate::system_core::internals::MessageToClient;
use crate::system_core::permissions::Permissions;
use crate::database::DATABASE;

pub fn unblock() -> commands::Command {
    async fn logic(ctx: &commands::Context) -> commands::CommandResponse {
        let user = ctx.args[0].as_str();

        let blocked_users = DATABASE.get_val_from_user(&ctx.executor.username, "blocked").await;

        if blocked_users.is_none() {
            return Err(format!("{BOLD}{YELLOW}You have not yet blocked a user{C_RESET}"))
        }

        let blocked_users = blocked_users.unwrap().replace(format!("{user},").as_str(), "");
        DATABASE.update_val(&ctx.executor.username, "blocked", &blocked_users).await.unwrap();

        ctx.tx_channel.send(MessageToClient::SystemMessage {
            content: format!("{BOLD}{LIGHT_GREEN}Unblocked {user}{C_RESET}")
        }).await.unwrap();

        Ok(None)
    }

    commands::Command {
        name: "unblock".to_string(),
        aliases: vec![],
        description: "Unblock a user".to_string(),
        category: CommandCategory::User,
        permissions: Permissions::Member,
        required_args: 1,
        handler: |ctx| Box::pin(async move {
            logic(&ctx).await
        }),
    }
}