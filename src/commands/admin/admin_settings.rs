use sqlx::Row;
use tokio::spawn;

use stblib::utilities::{contains_whitespace, escape_ansi};
use stblib::colors::{BOLD, C_RESET, GRAY, GREEN, LIGHT_GREEN, MAGENTA, RED, RESET, UNDERLINE, YELLOW};

use crate::system_core::commands;
use crate::system_core::commands::CommandCategory;
use crate::system_core::permissions::Permissions;
use crate::system_core::string::{bool_color_fmt, string_to_bool};
use crate::system_core::hooks::Hook;
use crate::system_core::internals::MessageToClient;
use crate::system_core::server_core::Event;
use crate::security::verification::MessageAction;
use crate::utilities::{is_valid_username, role_color_parser};
use crate::database::db::DATABASE;
use crate::database::Database;
use crate::constants::messages::{ADMIN_SETTINGS_HELP, USER_SETTINGS_HELP};
use crate::constants::chars::USERNAME_ALLOWED_CHARS;
use crate::constants::log_messages::{WRITE_PACKET_FAIL};
use crate::global::{CONFIG, LOGGER, MESSAGE_VERIFICATOR};


#[allow(clippy::too_many_lines)]
pub fn admin_settings() -> commands::Command {
    async fn logic(ctx: &commands::Context) -> commands::CommandResponse {
        match ctx.args[0].as_str() {
            "help" => Ok(Some(ADMIN_SETTINGS_HELP.to_string())),

            "role" => {
                if ctx.args[1..].is_empty() {
                    return Err(format!("Missing arguments - Subcommand requires at least 2 argument - Got {} arguments", ctx.args[1..].len()))
                }

                let username = ctx.args[1].as_str();
                let role = ctx.args[2].as_str().to_lowercase();

                if !["member", "bot", "admin"].contains(&role.as_str()) {
                    return Err("Invalid role!".to_string())
                }

                match sqlx::query("UPDATE users SET role = ? WHERE username = ?")
                    .bind(&role)
                    .bind(username)
                    .execute(&DATABASE.connection)
                    .await {
                    Ok(..) => ..,
                    Err(_) => return Ok(Some(format!("{BOLD}{RED}Sorry, this user does not exist!{C_RESET}")))
                };

                Ok(None)
            },
            "badge" => {
                if ctx.args[1..].is_empty() {
                    return Err(format!("Missing arguments - Subcommand requires at least 3 argument - Got {} arguments", ctx.args[1..].len()))
                }

                let subcommand = ctx.args[1].as_str();

                match subcommand {
                    "set" => {
                        let username = ctx.args[2].as_str();
                        let badge = ctx.args[3].as_str();

                        if badge == "reset" || badge == "remove" {
                            match sqlx::query("UPDATE users SET badge = '' WHERE username = ?")
                                .bind(username)
                                .execute(&DATABASE.connection)
                                .await {
                                Ok(..) => ..,
                                Err(_) => return Ok(Some(format!("{BOLD}{RED}Sorry, this user does not exist!{C_RESET}")))
                            };

                            return Ok(Some(format!("{BOLD}{LIGHT_GREEN}Removed badge of {username}{C_RESET}")))
                        }

                        let badges: String = sqlx::query("SELECT badges FROM users WHERE username = ?")
                            .bind(username)
                            .fetch_one(&DATABASE.connection)
                            .await.unwrap().get("badges");

                        if !badges.contains(badge) {
                            return Ok(Some(format!("{BOLD}{RED}This user does not own this badge!{C_RESET}")))
                        }

                        match sqlx::query("UPDATE users SET badge = ? WHERE username = ?")
                            .bind(badge)
                            .bind(username)
                            .execute(&DATABASE.connection)
                            .await {
                            Ok(..) => ..,
                            Err(_) => return Ok(Some(format!("{BOLD}{RED}Sorry, this user does not exist!{C_RESET}")))
                        };

                    },
                    _ => return Err(format!("{RED}{BOLD}Invalid subcommand!{C_RESET}"))
                }

                Ok(None)
            },

            _ => Err(format!("{RED}{BOLD}Invalid subcommand!{C_RESET}")),
        }
    }

    commands::Command {
        name: "admin-settings".to_string(),
        aliases: vec![],
        description: "Change some settings of other's account".to_string(),
        category: CommandCategory::Admin,
        permissions: Permissions::Admin,
        required_args: 1,
        handler: |ctx| Box::pin(async move {
            logic(&ctx).await
        }),
    }
}