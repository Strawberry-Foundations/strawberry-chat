use stblib::colors::{BOLD, C_RESET, CYAN, GREEN, UNDERLINE};
use crate::database::db::DATABASE;

use crate::system_core::commands;
use crate::system_core::commands::CommandCategory;
use crate::system_core::internals::MessageToClient;
use crate::system_core::permissions::Permissions;
use crate::global::CONFIG;

pub fn members() -> commands::Command {
    async fn logic(ctx: &commands::Context) -> commands::CommandResponse {
        let members_vec: Vec<String> = sqlx::query_scalar("SELECT username FROM users")
            .fetch_all(&DATABASE.connection)
            .await.unwrap();

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
        handler: |ctx| Box::pin(async move {
            logic(&ctx).await
        }),
    }
}