use stblib::colors::{BOLD, C_RESET, CYAN, GREEN, UNDERLINE};

use crate::system_core::commands;
use crate::system_core::commands::CommandCategory;
use crate::system_core::internals::MessageToClient;
use crate::system_core::permissions::Permissions;
use crate::system_core::server_core::get_online_usernames;
use crate::global::CONFIG;

pub fn online() -> commands::Command {
    async fn logic(ctx: &commands::Context) -> commands::CommandResponse {
        let online_users_vec = get_online_usernames().await.clone();

        let online_users = if CONFIG.config.max_users == -1 {
            format!("{}", online_users_vec.len())
        } else {
            format!("{}/{}", online_users_vec.len(), CONFIG.config.max_users)
        };

        let message = format!("{GREEN}{BOLD}{UNDERLINE}Users who are currently online ({online_users}){C_RESET}
        {BOLD}->{C_RESET} {CYAN}{}{C_RESET}", online_users_vec.join(", ")
        );

        ctx.tx_channel.send(MessageToClient::SystemMessage {
            content: message
        }).await.unwrap();

        Ok(None)
    }

    commands::Command {
        name: "online".to_string(),
        aliases: vec![],
        description: "Shows online users".to_string(),
        category: CommandCategory::User,
        permissions: Permissions::Member,
        handler: |ctx| Box::pin(async move {
            logic(&ctx).await
        }),
    }
}