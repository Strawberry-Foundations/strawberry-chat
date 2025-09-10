use libstrawberry::colors::{BLUE, BOLD, C_RESET, CYAN, GREEN, RESET, UNDERLINE};

use crate::system_core::commands;
use crate::system_core::commands::CommandCategory;
use crate::system_core::internals::MessageToClient;
use crate::system_core::permissions::Permissions;
use crate::global::{AUTHORS, CHAT_NAME, CODENAME, CORE_VERSION, DEFAULT_VERSION, EXT_VERSION, SERVER_EDITION};

pub fn about() -> commands::Command {
    async fn logic(ctx: &commands::Context) -> commands::CommandResponse {
        let message = format!("
    {GREEN}{BOLD}{UNDERLINE}About {CHAT_NAME}{C_RESET}
  * {CYAN}{BOLD}Thank you for using {CHAT_NAME}!{C_RESET}
  * {BLUE}{BOLD}Version:{RESET} {} {CODENAME} ({SERVER_EDITION}) ({}){RESET}{C_RESET}
  * {BLUE}{BOLD}Core Version:{RESET} {}{RESET}{C_RESET}
  * {BLUE}{BOLD}Author:{RESET} {} {RESET}{C_RESET}

  - {BLUE}{CYAN}https://github.com/Strawberry-Foundations/strawberry-chat{C_RESET}",
        *DEFAULT_VERSION, *EXT_VERSION, *CORE_VERSION, AUTHORS.join(", "));


        ctx.tx_channel.send(MessageToClient::SystemMessage {
            content: message
        }).await.unwrap();

        Ok(None)
    }

    commands::Command {
        name: "about".to_string(),
        aliases: vec![],
        description: "Shows about description for Strawberry Chat".to_string(),
        category: CommandCategory::Default,
        permissions: Permissions::Member,
        required_args: 0,
        handler: |ctx| Box::pin(async move {
            logic(&ctx).await
        }),
    }
}