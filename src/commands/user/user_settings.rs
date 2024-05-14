use sqlx::Row;
use stblib::colors::{BOLD, C_RESET, GRAY, GREEN, LIGHT_GREEN, MAGENTA, RED, RESET, UNDERLINE};

use crate::system_core::commands;
use crate::system_core::commands::CommandCategory;
use crate::system_core::permissions::Permissions;
use crate::system_core::string::{bool_color_fmt, string_to_bool};
use crate::utilities::role_color_parser;
use crate::database::db::DATABASE;
use crate::constants::messages::USER_SETTINGS_HELP;

#[allow(clippy::too_many_lines)]
pub fn user_settings() -> commands::Command {
    async fn logic(ctx: &commands::Context) -> commands::CommandResponse {
        match ctx.args[0].as_str() {
            "help" => Ok(Some(USER_SETTINGS_HELP.to_string())),
            "preview" => {
                let user_settings = DATABASE.get_account_by_name(&ctx.executor.username).await.unwrap();

                Ok(Some(format!(
                    "
    {MAGENTA}{BOLD}{UNDERLINE}User Settings - Preview{C_RESET}
    {GRAY}* {GREEN}{BOLD}Direct Messages{RESET}{GRAY} - {RESET}{}{C_RESET}
    {GRAY}* {GREEN}{BOLD}Discord username{RESET}{GRAY} - {RESET}{}{C_RESET}
    {GRAY}* {GREEN}{BOLD}Strawberry ID{RESET}{GRAY} - {RESET}{}{C_RESET}
    {GRAY}* {GREEN}{BOLD}Role color{RESET}{GRAY} - {RESET}{}{}{C_RESET}
    {GRAY}* {GREEN}{BOLD}Badge{RESET}{GRAY} - {RESET}{}{C_RESET}
    {GRAY}* {GREEN}{BOLD}Description{RESET}{GRAY} - {RESET}{}{C_RESET}
                ",
                    bool_color_fmt(user_settings.enable_dms),
                    user_settings.discord_name,
                    user_settings.strawberry_id,
                    role_color_parser(user_settings.role_color.as_str()), user_settings.role_color,
                    user_settings.badge,
                    user_settings.description,
                )))
            },
            "allow-dms" => {
                if ctx.args[1].is_empty() {
                    return Err(format!("{RED}{BOLD}Missing arguments - Subcommand requires at least 1 argument - Got 0 arguments{C_RESET}"))
                }

                sqlx::query("UPDATE users SET enable_dms = ? WHERE username = ?")
                    .bind(string_to_bool(&ctx.args[1]))
                    .bind(&ctx.executor.username)
                    .execute(&DATABASE.connection)
                    .await
                    .unwrap_or_else(|err| { println!("{err}"); std::process::exit(1) });

                if string_to_bool(&ctx.args[1]) {
                    Ok(Some(format!("{LIGHT_GREEN}You can now receive direct messages from other users.")))
                }
                else {
                    Ok(Some(format!("{LIGHT_GREEN}You can no longer receive direct messages from other users.")))
                }

            },

            "role-color" => {
                if ctx.args[1].is_empty() {
                    return Err("Missing arguments - Subcommand requires at least 1 argument - Got 0 arguments".to_string())
                }

                sqlx::query("UPDATE users SET role_color = ? WHERE username = ?")
                    .bind(&ctx.args[1])
                    .bind(&ctx.executor.username)
                    .execute(&DATABASE.connection)
                    .await
                    .unwrap_or_else(|err| { println!("{err}"); std::process::exit(1) });

                Ok(Some(format!("{LIGHT_GREEN}Updated role color to {}{}{C_RESET}", role_color_parser(&ctx.args[1]), &ctx.args[1])))
            },

            "discord" => {
                if ctx.args[1..].is_empty() {
                    return (sqlx::query("SELECT discord_name FROM users WHERE username = ?")
                        .bind(&ctx.executor.username)
                        .fetch_one(&DATABASE.connection)
                        .await).map_or_else(|_| Ok(Some(format!("{BOLD}{RED}Sorry, this user does not exist!{C_RESET}"))), |res| {
                        let discord_name: String = res.get("discord_name");
                        Ok(Some(format!("{BOLD}{LIGHT_GREEN}Your current Discord Name: {RESET}{discord_name}{C_RESET}")))
                    });
                }


                if ctx.args[1].as_str() == "reset" || ctx.args[0].as_str() == "remove" {
                    match sqlx::query("UPDATE users SET discord_name = '' WHERE username = ?")
                        .bind(&ctx.executor.username)
                        .execute(&DATABASE.connection)
                        .await {
                        Ok(..) => ..,
                        Err(_) => return Ok(Some(format!("{BOLD}{RED}Sorry, this user does not exist!{C_RESET}")))
                    };

                    return Ok(Some(format!("{BOLD}{LIGHT_GREEN}Removed Discord Name. Rejoin to apply changes{C_RESET}")))
                }

                let discord_name = ctx.args[1..].to_vec().join(" ");

                match sqlx::query("UPDATE users SET discord_name = ? WHERE username = ?")
                    .bind(&discord_name)
                    .bind(&ctx.executor.username)
                    .execute(&DATABASE.connection)
                    .await {
                    Ok(..) => ..,
                    Err(_) => return Ok(Some(format!("{BOLD}{RED}Sorry, this user does not exist!{C_RESET}")))
                };

                Ok(Some(format!(
                    "{BOLD}{LIGHT_GREEN}Changed Discord Name to {}{discord_name}{C_RESET}{BOLD}{LIGHT_GREEN}. \
                    Rejoin to apply changes{C_RESET}", role_color_parser(&ctx.executor.role_color)
                )))
            },

            "badge" => {
                if ctx.args[1].is_empty() {
                    return Err("Missing arguments - Subcommand requires at least 1 argument - Got 0 arguments".to_string())
                }

                sqlx::query("UPDATE users SET discord_name = ? WHERE username = ?")
                    .bind(&ctx.args[1])
                    .bind(&ctx.executor.username)
                    .execute(&DATABASE.connection)
                    .await
                    .unwrap_or_else(|err| { println!("{err}"); std::process::exit(1) });

                Ok(Some(format!("{LIGHT_GREEN}Updated Discord name to {}{}{C_RESET}", role_color_parser(&ctx.args[1]), &ctx.args[1])))
            },

            _ => Err(format!("{RED}{BOLD}Invalid subcommand!{C_RESET}")),
        }
    }

    commands::Command {
        name: "settings".to_string(),
        aliases: vec![],
        description: "Change some settings of your account".to_string(),
        category: CommandCategory::User,
        permissions: Permissions::Member,
        required_args: 1,
        handler: |ctx| Box::pin(async move {
            logic(&ctx).await
        }),
    }
}