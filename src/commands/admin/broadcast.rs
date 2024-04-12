use stblib::colors::{BOLD, CYAN, GREEN, RED, UNDERLINE};

use crate::system_core::commands;
use crate::system_core::commands::CommandCategory;
use crate::system_core::permissions::Permissions;
use crate::system_core::string::StbString;

pub fn broadcast() -> commands::Command {
    async fn logic(ctx: &commands::Context) -> commands::CommandResponse {
        if ctx.args.is_empty() {
            return Ok(Some(format!("{RED}{BOLD}Missing arguments - Command requires at least 1 argument - Got 0 arguments")))
        }
        
        let content = StbString::from_str(ctx.args[0..].to_vec().join(" ")).apply_htpf();

        Ok(None)
    }

    commands::Command {
        name: "broadcast".to_string(),
        aliases: vec![],
        description: "Broadcasts a message".to_string(),
        category: CommandCategory::Admin,
        permissions: Permissions::Admin,
        handler: |ctx| Box::pin(async move {
            logic(&ctx).await
        }),
    }
}