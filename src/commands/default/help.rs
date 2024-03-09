use stblib::colors::{BLUE, BOLD, C_RESET, CYAN, GREEN, MAGENTA, RED, RESET, UNDERLINE};
use crate::system_core::commands;
use crate::system_core::commands::{CommandCategory, get_commands_category};
use crate::system_core::message::MessageToClient;
use crate::system_core::permissions::Permissions;

pub fn help() -> commands::Command {
    async fn logic(ctx: &commands::Context) -> commands::CommandResponse {
        let default_help_message: String = get_commands_category(&CommandCategory::Default)
            .iter()
            .map(|cmd| format!("{BLUE}{BOLD}/{}: {RESET}{}{C_RESET}", cmd.name, cmd.description))
            .collect::<Vec<String>>()
            .join("\n        ");

        let user_help_message: String = get_commands_category(&CommandCategory::User)
            .iter()
            .map(|cmd| format!("{BLUE}{BOLD}/{}: {RESET}{}{C_RESET}", cmd.name, cmd.description))
            .collect::<Vec<String>>()
            .join("\n        ");

        let etc_help_message: String = get_commands_category(&CommandCategory::Etc)
            .iter()
            .map(|cmd| format!("{BLUE}{BOLD}/{}: {RESET}{}{C_RESET}", cmd.name, cmd.description))
            .collect::<Vec<String>>()
            .join("\n        ");
        
        let admin_help_message: String = get_commands_category(&CommandCategory::Admin)
            .iter()
            .map(|cmd| format!("{BLUE}{BOLD}/{}: {RESET}{}{C_RESET}", cmd.name, cmd.description))
            .collect::<Vec<String>>()
            .join("\n        ");

        let help_message = format!("{GREEN}{UNDERLINE}{BOLD}Default commands{C_RESET}
        {default_help_message}

        {CYAN}{UNDERLINE}{BOLD}Profile & User Commands{C_RESET}
        {user_help_message}
        
        {MAGENTA}{UNDERLINE}{BOLD}Admin Commands{C_RESET}
        {admin_help_message}

        {RED}{UNDERLINE}{BOLD}Other Commands{C_RESET}
        {etc_help_message}
        ");

        ctx.tx_channel.send(MessageToClient::SystemMessage {
            content: help_message
        }).await.unwrap();

        Ok(None)
    }

    commands::Command {
        name: "help".to_string(),
        aliases: vec![],
        description: "Help command".to_string(),
        category: CommandCategory::Default,
        permissions: Permissions::Member,
        handler: |ctx| Box::pin(async move {
            logic(&ctx).await
        }),
    }
}