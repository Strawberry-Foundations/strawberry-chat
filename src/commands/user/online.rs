use stblib::colors::{BOLD, C_RESET, CYAN, GREEN, UNDERLINE};

use crate::global::CONFIG;
use crate::system_core::{commands, CORE};
use crate::system_core::message::MessageToClient;
use crate::system_core::server_core::{get_online_users, get_users_len};

pub fn online() -> commands::Command {
    async fn logic(ctx: &commands::Context) -> commands::CommandResponse {
        let online_users = if CONFIG.config.max_users == -1 {
            format!("{}", CORE.read().await.online_users)
        } else {
            format!("{}/{}", CORE.read().await.online_users, CONFIG.config.max_users)
        };

        let message = format!("{GREEN}{BOLD}{UNDERLINE}Users who are currently online ({online_users}){C_RESET}
        {BOLD}->{C_RESET} {CYAN}{}{C_RESET}
        ", "" // get_online_users().await.iter().filter_map(|c| c.get_user().map(|u| u.username)).collect::<Vec<String>>().join(", ")
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
        handler: |ctx| Box::pin(async move {
            logic(&ctx).await
        }),
    }
}