use stblib::colors::{BOLD, C_RESET, YELLOW};

use crate::system_core::commands;
use crate::system_core::commands::CommandCategory;
use crate::system_core::internals::MessageToClient;
use crate::system_core::permissions::Permissions;

pub fn delete_account() -> commands::Command {
    async fn logic(ctx: &commands::Context) -> commands::CommandResponse {
        ctx.tx_channel.send(MessageToClient::SystemMessage {
            content: format!("{YELLOW}{BOLD}Are you sure you want to delete your user account? This action is irreversible!!{C_RESET}")
        }).await.unwrap();
        
        

        Ok(None)
    }

    commands::Command {
        name: "deleteaccount".to_string(),
        aliases: vec!["delaccount"],
        description: "Delete your account on this server".to_string(),
        category: CommandCategory::User,
        permissions: Permissions::Member,
        handler: |ctx| Box::pin(async move {
            logic(&ctx).await
        }),
    }
}