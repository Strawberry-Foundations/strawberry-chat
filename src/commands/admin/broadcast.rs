use stblib::colors::{BOLD, RED};

use crate::system_core::commands;
use crate::system_core::commands::CommandCategory;
use crate::system_core::internals::MessageToClient;
use crate::system_core::permissions::Permissions;
use crate::system_core::server_core::send_to_all;
use crate::system_core::string::StbString;

pub fn broadcast() -> commands::Command {
    async fn logic(ctx: &commands::Context) -> commands::CommandResponse {
        let content = StbString::from_str(ctx.args[0..].to_vec().join(" ")).apply_htpf();

        send_to_all(MessageToClient::SystemMessage { content: content.to_string() }, true).await;

        Ok(None)
    }

    commands::Command {
        name: "broadcast".to_string(),
        aliases: vec![],
        description: "Broadcasts a message".to_string(),
        category: CommandCategory::Admin,
        permissions: Permissions::Admin,
        required_args: 1,
        handler: |ctx| Box::pin(async move {
            logic(&ctx).await
        }),
    }
}