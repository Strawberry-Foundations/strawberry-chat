use chrono::DateTime;
use stblib::colors::{BOLD, C_RESET, CYAN, GREEN, RED, UNDERLINE, RESET, MAGENTA};

use crate::system_core::commands;
use crate::system_core::commands::CommandCategory;
use crate::system_core::internals::MessageToClient;
use crate::system_core::permissions::Permissions;
use crate::system_core::string::capitalize_first;
use crate::system_core::server_core::STATUS;
use crate::database::db::DATABASE;
use crate::utilities::{create_badge_list, parse_user_status, role_color_parser};

#[derive(Clone, Default, Debug, PartialEq, Eq, sqlx::FromRow)]
pub struct UUserAccount {
    pub user_id: i32,
    pub username: String,
    pub nickname: String,
    pub description: String,
    pub badge: String,
    pub badges: String,
    pub role: String,
    pub role_color: String,
    pub strawberry_id: String,
    pub discord_name: String,
    pub creation_date: i32,
}

pub fn userinfo() -> commands::Command {
    async fn logic(ctx: &commands::Context) -> commands::CommandResponse {
        let username = if ctx.args.is_empty() {
            &ctx.executor.username
        } else {
            ctx.args[0].as_str()
        };

        if !DATABASE.is_username_taken(&username.to_string()).await {
            return Err(format!("{BOLD}{RED}Sorry, this user does not exist!{C_RESET}"))
        }

        let mut user: UUserAccount = sqlx::query_as(
            "SELECT username, nickname, badge, role, role_color, description, badges, discord_name, user_id, strawberry_id, creation_date FROM users WHERE LOWER(username) = ?"
        )
            .bind(username)
            .fetch_one(&DATABASE.connection)
            .await.unwrap();

        if user.nickname.is_empty() {
            user.nickname = String::from("Not set");
        }
        if user.description.is_empty() {
            user.description = String::from("Not set");
        }
        if user.badge.is_empty() {
            user.badge = String::from("Not set");
        }
        if user.discord_name.is_empty() {
            user.discord_name = String::from("Not set");
        } else {
            user.discord_name = format!("{MAGENTA}@{}", user.discord_name);
        }
        if user.strawberry_id.is_empty() {
            user.strawberry_id = String::from("Not set");
        }

        user.role = capitalize_first(user.role.as_str());

        let date = DateTime::from_timestamp(i64::from(user.creation_date), 0).unwrap();

        let status_raw = *STATUS.read().await.get_by_name(user.username.as_str());
        let status = parse_user_status(status_raw, false);

        let message = format!(
            "
     {BOLD}{CYAN}{UNDERLINE}User profile of {}{C_RESET} {status}
  *  {BOLD}{GREEN}Username: {RESET}{}@{}{C_RESET}
  *  {BOLD}{GREEN}User-ID:{RESET} {}{C_RESET}
  *  {BOLD}{GREEN}Nickname:{RESET} {}{C_RESET}
  *  {BOLD}{GREEN}Description:{RESET} {}{C_RESET}
  *  {BOLD}{GREEN}Member since:{RESET} {}{C_RESET}
  *  {BOLD}{GREEN}Main Badge:{RESET} {}{C_RESET}
  *  {BOLD}{GREEN}Badges:{RESET} {}{C_RESET}
  *  {BOLD}{GREEN}Role:{RESET} {}{C_RESET}
  *  {BOLD}{GREEN}Role Color:{RESET} {}{}{C_RESET}
  *  {BOLD}{GREEN}Strawberry ID:{RESET} {}{C_RESET}
  *  {BOLD}{GREEN}Discord:{RESET} {}{C_RESET}
",
            user.username, role_color_parser(user.role_color.as_str()), user.username,
            user.user_id, user.nickname, user.description, date.format("%a, %e. %b %Y"), user.badge,
            create_badge_list(user.badges.as_str()), user.role, role_color_parser(user.role_color.as_str()),
            capitalize_first(user.role_color.as_str()), user.strawberry_id, user.discord_name

        );

        ctx.tx_channel.send(MessageToClient::SystemMessage {
            content: message
        }).await.unwrap();

        Ok(None)
    }

    commands::Command {
        name: "userinfo".to_string(),
        aliases: vec!["user", "member"],
        description: "Shows information about a user".to_string(),
        category: CommandCategory::User,
        permissions: Permissions::Member,
        required_args: 0,
        handler: |ctx| Box::pin(async move {
            logic(&ctx).await
        }),
    }
}