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
use crate::security::crypt::Crypt;
use crate::utilities::{is_valid_username, role_color_parser};
use crate::database::DATABASE;
use crate::constants::messages::USER_SETTINGS_HELP;
use crate::constants::chars::USERNAME_ALLOWED_CHARS;
use crate::constants::log_messages::{WRITE_PACKET_FAIL};
use crate::global::{CONFIG, LOGGER, MESSAGE_VERIFICATOR};

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
                    return sqlx::query("SELECT discord_name FROM users WHERE username = ?")
                        .bind(&ctx.executor.username)
                        .fetch_one(&DATABASE.connection)
                        .await.map_or_else(|_| Err(format!("{BOLD}{RED}Sorry, this user does not exist!{C_RESET}")), |res| {
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
                        Err(_) => return Err(format!("{BOLD}{RED}Sorry, this user does not exist!{C_RESET}"))
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
                    Err(_) => return Err(format!("{BOLD}{RED}Sorry, this user does not exist!{C_RESET}"))
                };

                Ok(Some(format!(
                    "{BOLD}{LIGHT_GREEN}Changed Discord Name to {}{discord_name}{C_RESET}{BOLD}{LIGHT_GREEN}. \
                    Rejoin to apply changes{C_RESET}", role_color_parser(&ctx.executor.role_color)
                )))
            },

            "badge" => {
                if ctx.args[1].as_str() == "reset" || ctx.args[1].as_str() == "remove" {
                    match sqlx::query("UPDATE users SET badge = '' WHERE username = ?")
                        .bind(&ctx.executor.username)
                        .execute(&DATABASE.connection)
                        .await {
                        Ok(..) => ..,
                        Err(_) => return Err(format!("{BOLD}{RED}Sorry, this user does not exist!{C_RESET}"))
                    };

                    return Ok(Some(format!("{BOLD}{LIGHT_GREEN}Removed badge. Rejoin to apply changes{C_RESET}")))
                }

                let badge = &ctx.args[1];


                let badges: String = sqlx::query("SELECT badges FROM users WHERE username = ?")
                    .bind(&ctx.executor.username)
                    .fetch_one(&DATABASE.connection)
                    .await.unwrap().get("badges");

                if !badges.contains(badge) {
                    return Err(format!("{BOLD}{RED}You do not own this badge!{C_RESET}"))
                }

                match sqlx::query("UPDATE users SET badge = ? WHERE username = ?")
                    .bind(badge)
                    .bind(&ctx.executor.username)
                    .execute(&DATABASE.connection)
                    .await {
                    Ok(..) => ..,
                    Err(_) => return Err(format!("{BOLD}{RED}Sorry, this user does not exist!{C_RESET}"))
                };

                Ok(Some(format!(
                        "{BOLD}{LIGHT_GREEN}Changed your main badge to {}{badge}{C_RESET}{BOLD}{LIGHT_GREEN}. \
                Rejoin to apply changes{C_RESET}",
                        role_color_parser(&ctx.executor.role_color)
                    )))
            },
            "account" => {
                if ctx.args[1..].is_empty() {
                    return Err(format!("Missing arguments - Subcommand requires at least 1 argument - Got {} arguments", ctx.args[1..].len()))
                }

                if ctx.args[1].as_str() == "username" && ctx.args.len() < 3 {
                    return Err("Missing arguments - Subcommand requires at least 1 argument - Got 0 arguments".to_string())
                }

                match ctx.args[1].as_str() {
                    "username" => {
                        let new_username = ctx.args[2].as_str();

                        if new_username == ctx.executor.username {
                            return Err(format!("{YELLOW}{BOLD}You shouldn't update your username to your current. Nothing changed.{C_RESET}"))
                        }

                        ctx.tx_channel.send(MessageToClient::SystemMessage {
                            content: format!("{YELLOW}{BOLD}Are you sure to change your username to {new_username}?{C_RESET}")
                        }).await.unwrap();

                        let mut hook = Hook::new(ctx.executor.clone(), ctx.tx_channel.clone(), 1).await;
                        
                        let new_username_cc = escape_ansi(new_username);
                        
                        spawn(async move {
                            if let Some(Event::UserMessage { content, .. }) = hook.rx.recv().await {
                                if escape_ansi(&content).eq_ignore_ascii_case("yes") {
                                    /// Check if the username is in blacklisted words
                                    let action = MESSAGE_VERIFICATOR.check(&new_username_cc.to_lowercase());

                                    match action {
                                        MessageAction::Kick | MessageAction::Hide => {
                                            hook.tx_ctx.send(MessageToClient::SystemMessage {
                                                content: format!("{YELLOW}{BOLD}This username is not allowed!{C_RESET}")
                                            }).await.unwrap_or_else(|_| LOGGER.warning(WRITE_PACKET_FAIL));

                                            return;
                                        },
                                        _ => {}
                                    }

                                    /// If username is in this set of blacklisted words, return an error message
                                    if ["exit", "register", "login", "sid"].contains(&new_username_cc.as_str()) {
                                        hook.tx_ctx.send(MessageToClient::SystemMessage {
                                            content: format!("{YELLOW}{BOLD}This username is not allowed!{C_RESET}")
                                        }).await.unwrap_or_else(|_| LOGGER.warning(WRITE_PACKET_FAIL));

                                        return;

                                    }

                                    /// If username contains whitespaces, return an error message
                                    if contains_whitespace(&new_username_cc) {
                                        hook.tx_ctx.send(MessageToClient::SystemMessage {
                                            content: format!("{YELLOW}{BOLD}Your username must not contain spaces{C_RESET}")
                                        }).await.unwrap_or_else(|_| LOGGER.warning(WRITE_PACKET_FAIL));

                                        return;
                                    }

                                    /// If username character is not in our charset, return an error message
                                    if !is_valid_username(new_username_cc.as_str(), USERNAME_ALLOWED_CHARS) {
                                        hook.tx_ctx.send(MessageToClient::SystemMessage {
                                            content: format!("{YELLOW}{BOLD}Please use only lowercase letters, numbers, dots or underscores{C_RESET}")
                                        }).await.unwrap_or_else(|_| LOGGER.warning(WRITE_PACKET_FAIL));

                                        return;
                                    }

                                    /// If username is longer than `max_username_length` (default: 32) characters, return an error message
                                    if new_username_cc.len() > CONFIG.config.max_username_length as usize {
                                        hook.tx_ctx.send(MessageToClient::SystemMessage {
                                            content: format!("{YELLOW}{BOLD}Your username is too long{C_RESET}")
                                        }).await.unwrap_or_else(|_| LOGGER.warning(WRITE_PACKET_FAIL));

                                        return;
                                    }

                                    /// Check if username is already taken
                                    if DATABASE.is_username_taken(&new_username_cc).await {
                                        hook.tx_ctx.send(MessageToClient::SystemMessage {
                                            content: format!("{YELLOW}{BOLD}This username is already in use!{C_RESET}")
                                        }).await.unwrap_or_else(|_| LOGGER.warning(WRITE_PACKET_FAIL));

                                        return;
                                    }

                                    sqlx::query("UPDATE users SET username = ? WHERE username = ?")
                                        .bind(&new_username_cc)
                                        .bind(&hook.user.username)
                                        .execute(&DATABASE.connection)
                                        .await
                                        .unwrap_or_else(|err| { println!("{err}"); std::process::exit(1) });
                                    
                                    hook.tx_ctx.send(MessageToClient::SystemMessage {
                                        content: format!("{GREEN}{BOLD}Your username has been updated to {new_username_cc}. You may need to rejoin in Strawberry Chat{C_RESET}")
                                    }).await.unwrap();

                                } else {
                                    hook.tx_ctx.send(MessageToClient::SystemMessage {
                                        content: format!("{YELLOW}{BOLD}Cancelled{C_RESET}")
                                    }).await.unwrap();
                                }
                            }
                        });
                    },
                    "password" => {
                        ctx.tx_channel.send(MessageToClient::SystemMessage {
                            content: format!("{GREEN}{BOLD}Enter new password: {C_RESET}")
                        }).await.unwrap();
                        
                        let mut hook = Hook::new(ctx.executor.clone(), ctx.tx_channel.clone(), 1).await;
                        
                        spawn(async move {
                            if let Some(Event::UserMessage { content, .. }) = hook.rx.recv().await {
                                /// If password contains whitespaces, return an error message
                                if contains_whitespace(&content) {
                                    hook.tx_ctx.send(MessageToClient::SystemMessage {
                                        content: format!("{YELLOW}{BOLD}Your password must not contain spaces{C_RESET}")
                                    }).await.unwrap_or_else(|_| LOGGER.warning(WRITE_PACKET_FAIL));

                                    return;
                                }

                                /// If password is longer than `max_password_length` (default: 256) characters, return an error message
                                if content.len() > CONFIG.config.max_password_length as usize {
                                    hook.tx_ctx.send(MessageToClient::SystemMessage {
                                        content: format!("{YELLOW}{BOLD}Your password is too long{C_RESET}")
                                    }).await.unwrap_or_else(|_| LOGGER.warning(WRITE_PACKET_FAIL));
                                }

                                let mut hook = Hook::new(hook.user, hook.tx_ctx, hook.uses).await;

                                let first_password = content.clone();

                                if let Some(Event::UserMessage { content, .. }) = hook.rx.recv().await {
                                    hook.tx_ctx.send(MessageToClient::SystemMessage {
                                        content: format!("{GREEN}{BOLD}Confirm password: {C_RESET}")
                                    }).await.unwrap_or_else(|_| LOGGER.warning(WRITE_PACKET_FAIL));

                                    if first_password != content {
                                        hook.tx_ctx.send(MessageToClient::SystemMessage {
                                            content: format!("{YELLOW}{BOLD}Passwords do not match{C_RESET}")
                                        }).await.unwrap_or_else(|_| LOGGER.warning(WRITE_PACKET_FAIL));
                                    }
                                    
                                    let password = Crypt::hash_password(content.as_str());

                                    sqlx::query("UPDATE users SET password = ? WHERE username = ?")
                                        .bind(&password)
                                        .bind(&hook.user.username)
                                        .execute(&DATABASE.connection)
                                        .await
                                        .unwrap_or_else(|err| { println!("{err}"); std::process::exit(1) });

                                    hook.tx_ctx.send(MessageToClient::SystemMessage {
                                        content: format!("{GREEN}{BOLD}Your password has been updated{C_RESET}")
                                    }).await.unwrap_or_else(|_| LOGGER.warning(WRITE_PACKET_FAIL));
                                }
                            }
                        });
                    },
                    _ => return Err(format!("{RED}{BOLD}Invalid subcommand!{C_RESET}"))
                }
                Ok(None)
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