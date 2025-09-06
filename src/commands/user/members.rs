use libstrawberry::colors::{BOLD, C_RESET, CYAN, GREEN, UNDERLINE};

use crate::system_core::commands;
use crate::system_core::commands::CommandCategory;
use crate::system_core::internals::MessageToClient;
use crate::system_core::permissions::Permissions;
use crate::global::CONFIG;
use crate::database::DATABASE;


pub fn members() -> commands::Command {
    async fn logic(ctx: &commands::Context) -> commands::CommandResponse {
        let members_vec = DATABASE.get_members().await;

        let members = if CONFIG.config.max_registered_users == -1 {
            format!("{}", members_vec.len())
        } else {
            format!("{}/{}", members_vec.len(), CONFIG.config.max_registered_users)
        };

        let message = format!("{GREEN}{BOLD}{UNDERLINE}Members on this server ({members}){C_RESET}
        {BOLD}->{C_RESET} {CYAN}{}{C_RESET}", members_vec.join(", ")
        );

        ctx.tx_channel.send(MessageToClient::SystemMessage {
            content: message
        }).await.unwrap();

        Ok(None)
    }

    commands::Command {
        name: "members".to_string(),
        aliases: vec![],
        description: "Shows registered members on this server".to_string(),
        category: CommandCategory::User,
        permissions: Permissions::Member,
        required_args: 0,
        handler: |ctx| Box::pin(async move {
            logic(&ctx).await
        }),
    }
}