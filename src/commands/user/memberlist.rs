use stblib::colors::{BOLD, C_RESET, CYAN, RED, UNDERLINE, RESET, MAGENTA, YELLOW, LIGHT_YELLOW, LIGHT_MAGENTA, LIGHT_RED};

use crate::system_core::commands;
use crate::system_core::commands::CommandCategory;
use crate::system_core::internals::MessageToClient;
use crate::system_core::permissions::Permissions;
use crate::system_core::server_core::{get_online_usernames, STATUS};
use crate::database::DATABASE;
use crate::utilities::parse_user_status;

async fn format_to_list(member_list: &[String], fmt_color: &str) -> String {
    let futures = member_list.iter().map(|result| {
        async {
            let user = DATABASE.get_user_by_name(result).await.unwrap();

            let badge = if user.badge.is_empty() {
                String::new()
            } else {
                format!("[{}]", user.badge)
            };


            let username = if user.nickname.is_empty() {
                String::from(&user.username)
            } else {
                format!("{} (@{})", user.nickname, user.username)
            };

            let status_raw = *STATUS.read().await.get_by_name(user.username.as_str());
            let status_symbol = parse_user_status(status_raw).0;

            format!("{C_RESET}{status_symbol}{fmt_color} {username} {badge}")
        }
    });

    let formatted_results = futures::future::join_all(futures).await;
    formatted_results.join("\n           ")
}


pub fn memberlist() -> commands::Command {
    async fn logic(ctx: &commands::Context) -> commands::CommandResponse {
        let raw_members = DATABASE.get_members_by_role("member").await;

        let members: String = format_to_list(&raw_members, LIGHT_YELLOW).await;

        let raw_bots: Vec<String> = DATABASE.get_members_by_role("bot").await;

        let bots: String = format_to_list(&raw_bots, LIGHT_MAGENTA).await;

        let raw_admins: Vec<String> = DATABASE.get_members_by_role("admin").await;

        let admins: String = format_to_list(&raw_admins, LIGHT_RED).await;

        let members_total = DATABASE.get_members().await.len();
        let online_users = get_online_usernames().await.len();


        let message = format!(
            "
        {CYAN}{UNDERLINE}({members_total} Members, {online_users} Online){C_RESET}
        {BOLD}->{C_RESET} {RED}Administrators ({}){RESET}
           {LIGHT_RED}{admins}{RESET}

        {BOLD}->{RESET} {MAGENTA}Bots ({}){RESET}
           {LIGHT_MAGENTA}{bots}{RESET}

        {BOLD}->{C_RESET} {YELLOW}Members ({}){RESET}
           {LIGHT_YELLOW}{members}{RESET}",
            raw_admins.len(), raw_bots.len(), raw_members.len()

        );


        ctx.tx_channel.send(MessageToClient::SystemMessage {
            content: message
        }).await.unwrap();

        Ok(None)
    }

    commands::Command {
        name: "memberlist".to_string(),
        aliases: vec!["userlist", "users"],
        description: "Displays a list of members with their badges and roles".to_string(),
        category: CommandCategory::User,
        permissions: Permissions::Member,
        required_args: 0,
        handler: |ctx| Box::pin(async move {
            logic(&ctx).await
        }),
    }
}