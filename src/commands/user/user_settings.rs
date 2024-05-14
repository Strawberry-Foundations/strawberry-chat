use sqlx::Row;
use stblib::colors::{BOLD, C_RESET, LIGHT_GREEN, RED, RESET};

use crate::system_core::commands;
use crate::system_core::commands::CommandCategory;
use crate::system_core::permissions::Permissions;
use crate::system_core::string::{bool_color_fmt, string_to_bool};
use crate::utilities::role_color_parser;
use crate::database::db::DATABASE;
use crate::constants::messages::USER_SETTINGS_HELP;
use crate::system_core::internals::MessageToClient;

pub fn user_settings() -> commands::Command {
    async fn logic(ctx: &commands::Context) -> commands::CommandResponse {
        if ctx.args.is_empty() {
            return Ok(Some(format!("{RED}{BOLD}Missing arguments - Command requires at least 1 argument - Got 0 arguments{C_RESET}")))
        }

        match ctx.args[0].as_str() {
            "help" => Ok(Some(USER_SETTINGS_HELP.to_string())),
            "enable-dms" => {
                if ctx.args[1].is_empty() {
                    return Ok(Some(format!("{RED}{BOLD}Missing arguments - Subcommand requires at least 1 argument - Got 0 arguments{C_RESET}")))
                }

                sqlx::query("UPDATE users SET enable_dms = ? WHERE username = ?")
                    .bind(string_to_bool(&ctx.args[1]))
                    .bind(&ctx.executor.username)
                    .execute(&DATABASE.connection)
                    .await
                    .unwrap_or_else(|err| { println!("{err}"); std::process::exit(1) });

                Ok(Some(format!("{LIGHT_GREEN}Updated enable_dms to {}", bool_color_fmt(string_to_bool(&ctx.args[1])))))
            },

            "role-color" => {
                if ctx.args[1].is_empty() {
                    return Ok(Some(format!("{RED}{BOLD}Missing arguments - Subcommand requires at least 1 argument - Got 0 arguments{C_RESET}")))
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
                    return Ok(Some(format!("{RED}{BOLD}Missing arguments - Subcommand requires at least 1 argument - Got 0 arguments{C_RESET}")))
                }

                sqlx::query("UPDATE users SET discord_name = ? WHERE username = ?")
                    .bind(&ctx.args[1])
                    .bind(&ctx.executor.username)
                    .execute(&DATABASE.connection)
                    .await
                    .unwrap_or_else(|err| { println!("{err}"); std::process::exit(1) });

                Ok(Some(format!("{LIGHT_GREEN}Updated Discord name to {}{}{C_RESET}", role_color_parser(&ctx.args[1]), &ctx.args[1])))
            },
            
            _ => Ok(Some(format!("{RED}{BOLD}Invalid subcommand!{C_RESET}"))),
        }
    }

    commands::Command {
        name: "settings".to_string(),
        aliases: vec![],
        description: "Change some settings of your account".to_string(),
        category: CommandCategory::User,
        permissions: Permissions::Member,
        handler: |ctx| Box::pin(async move {
            logic(&ctx).await
        }),
    }
}