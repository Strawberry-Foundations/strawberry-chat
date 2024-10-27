use stblib::colors::{BOLD, C_RESET, RED, LIGHT_GREEN};

use crate::system_core::commands;
use crate::system_core::commands::CommandCategory;
use crate::system_core::internals::MessageToClient;
use crate::system_core::permissions::Permissions;
use crate::utilities::role_color_parser;
use crate::database::DATABASE;

pub fn badge() -> commands::Command {
    async fn logic(ctx: &commands::Context) -> commands::CommandResponse {
        if ctx.args[0].as_str() == "reset" || ctx.args[0].as_str() == "remove" {
            DATABASE.update_val(&ctx.executor.username, "badge", "").await.unwrap();
            return Ok(Some(format!("{BOLD}{LIGHT_GREEN}Removed badge. Rejoin to apply changes{C_RESET}")))
        }

        let badge = &ctx.args[0];

        let badges = DATABASE.get_val_from_user(&ctx.executor.username, "badges").await.unwrap();
        
        if !badges.contains(badge) {
            return Err(format!("{BOLD}{RED}You do not own this badge!{C_RESET}"))
        }

        DATABASE.update_val(&ctx.executor.username, "badge", badge).await.unwrap();

        ctx.tx_channel.send(MessageToClient::SystemMessage {
            content: format!(
                "{BOLD}{LIGHT_GREEN}Changed your main badge to {}{badge}{C_RESET}{BOLD}{LIGHT_GREEN}. \
                Rejoin to apply changes{C_RESET}",
                role_color_parser(&ctx.executor.role_color)
            )
        }).await.unwrap();

        Ok(None)
    }

    commands::Command {
        name: "badge".to_string(),
        aliases: vec![],
        description: "Set your main badge".to_string(),
        category: CommandCategory::User,
        permissions: Permissions::Member,
        required_args: 1,
        handler: |ctx| Box::pin(async move {
            logic(&ctx).await
        }),
    }
}