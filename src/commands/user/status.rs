use stblib::colors::{BOLD, C_RESET, GREEN};

use crate::system_core::commands;
use crate::system_core::commands::CommandCategory;
use crate::system_core::permissions::Permissions;
use crate::system_core::server_core::STATUS;
use crate::system_core::status::Status;
use crate::utilities::parse_user_status;

pub fn status() -> commands::Command {
    async fn logic(ctx: &commands::Context) -> commands::CommandResponse {
        if ctx.args.is_empty() {
            let status = *STATUS.read().await.get_by_name(ctx.executor.username.as_str());
            return Ok(Some(format!("{BOLD}{GREEN}Your current status: {C_RESET}{}", parse_user_status(status, true))))
        }

        let arg_status = &ctx.args[0];
        
        let status = match arg_status.to_lowercase().as_str() {
            "online" => Status::Online,
            "afk" => Status::Afk,
            "dnd" => Status::DoNotDisturb,
            _ => Status::default()
        };
        
        STATUS.write().await.append(ctx.executor.username.as_str(), status);

        Ok(Some(format!("{BOLD}{GREEN}Changed your status to {C_RESET}{}", parse_user_status(status, true))))
    }

    commands::Command {
        name: "status".to_string(),
        aliases: vec![],
        description: "Show or change your status".to_string(),
        category: CommandCategory::User,
        permissions: Permissions::Member,
        required_args: 1,
        handler: |ctx| Box::pin(async move {
            logic(&ctx).await
        }),
    }
}