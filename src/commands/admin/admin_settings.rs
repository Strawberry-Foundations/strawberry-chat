use stblib::colors::{BOLD, C_RESET, GREEN, LIGHT_GREEN, RED};

use crate::system_core::commands;
use crate::system_core::commands::CommandCategory;
use crate::system_core::permissions::Permissions;
use crate::database::DATABASE;
use crate::constants::messages::{ADMIN_SETTINGS_HELP};
use crate::constants::badges::BADGE_LIST;
use crate::utilities::create_badge_list;

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

                match DATABASE.update_val(&username, "role", &role).await {
                    Ok(..) => Ok(Some(format!("{GREEN}{BOLD}The role of {username} has been updated to '{role}'{C_RESET}"))),
                    Err(_) => Err(format!("{BOLD}{RED}Sorry, this user does not exist!{C_RESET}"))
                }
            },
            "badge" => {
                if ctx.args[1..].is_empty() {
                    return Err(format!("Missing arguments - Subcommand requires at least 3 argument - Got {} arguments", ctx.args[1..].len()))
                }

                let subcommand = ctx.args[1].as_str();

                match subcommand {
                    "set" => {
                        if ctx.args.len() < 4 {
                            return Err(format!("Missing arguments - Subcommand requires at least 3 argument - Got {} arguments", ctx.args[1..].len()))
                        }

                        let username = ctx.args[2].as_str();
                        let badge = ctx.args[3].as_str();

                        if badge == "reset" || badge == "remove" {
                            match DATABASE.update_val(&username,"badge", "").await {
                                Ok(..) => ..,
                                Err(_) => return Err(format!("{BOLD}{RED}Sorry, this user does not exist!{C_RESET}"))
                            };

                            return Ok(Some(format!("{BOLD}{LIGHT_GREEN}Removed badge of {username}{C_RESET}")))
                        }

                        let badges: String = match DATABASE.get_val_from_user(&username,"badges").await {
                            Some(val) => val,
                            None => return Err(format!("{BOLD}{RED}Sorry, this user does not exist!{C_RESET}"))
                        };

                        if !badges.contains(badge) {
                            return Err(format!("{BOLD}{RED}This user does not own this badge!{C_RESET}"))
                        }

                        match DATABASE.update_val(&username,"badge", badge).await {
                            Ok(..) => Ok(Some(format!("{GREEN}{BOLD}The main badge of {username} has been updated to '{badge}'{C_RESET}"))),
                            Err(_) => Err(format!("{BOLD}{RED}Sorry, this user does not exist!{C_RESET}"))
                        }

                    },
                    "add" => {
                        if ctx.args.len() < 4 {
                            return Err(format!("Missing arguments - Subcommand requires at least 3 argument - Got {} arguments", ctx.args[1..].len()))
                        }

                        let username = ctx.args[2].as_str();
                        let badge = ctx.args[3].as_str();

                        let badges = match DATABASE.get_val_from_user(&username, "badges").await {
                            Some(val) => val,
                            None => return Err(format!("{BOLD}{RED}Sorry, this user does not exist!{C_RESET}"))
                        };

                        if badges.contains(badge) {
                            return Err(format!("{BOLD}{RED}This user does already own this badge!{C_RESET}"))
                        }

                        if !BADGE_LIST.contains(&badge) {
                            return Err(format!("{BOLD}{RED}This badge does not exists!{C_RESET}"))
                        }

                        let new_badges = format!("{badges}{badge}");

                        match DATABASE.update_val(&username,"badges", &new_badges).await {
                            Ok(..) => Ok(Some(format!("{GREEN}{BOLD}Added badge '{badge}' to {username}'s profile{C_RESET}"))),
                            Err(_) => Err(format!("{BOLD}{RED}Sorry, this user does not exist!{C_RESET}"))
                        }

                    },
                    "remove" => {
                        let username = ctx.args[2].as_str();
                        let badge = ctx.args[3].as_str();

                        let badges = match DATABASE.get_val_from_user(&username, "badges").await {
                            Some(val) => val,
                            None => return Err(format!("{BOLD}{RED}Sorry, this user does not exist!{C_RESET}"))
                        };

                        if !badges.contains(badge) {
                            return Err(format!("{BOLD}{RED}This user does not own this badge!{C_RESET}"))
                        }

                        if !BADGE_LIST.contains(&badge) {
                            return Err(format!("{BOLD}{RED}This badge does not exists!{C_RESET}"))
                        }

                        let new_badges = badges.replace(badge, "");

                        match DATABASE.update_val(&username,"badges", &new_badges).await {
                            Ok(..) => Ok(Some(format!("{GREEN}{BOLD}Removed badge '{badge}' to {username}'s profile{C_RESET}"))),
                            Err(_) => Err(format!("{BOLD}{RED}Sorry, this user does not exist!{C_RESET}"))
                        }

                    },
                    _ => Err(format!("{RED}{BOLD}Invalid subcommand!{C_RESET}"))
                }
            },
            "list-badges" => {
                let badge_list =  create_badge_list(&BADGE_LIST.join(""));
                Ok(Some(format!("{GREEN}{BOLD}Available badges: {C_RESET}{badge_list}{C_RESET}")))
            }

            _ => Err(format!("{RED}{BOLD}Invalid subcommand!{C_RESET}")),
        }
    }

    commands::Command {
        name: "admin".to_string(),
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