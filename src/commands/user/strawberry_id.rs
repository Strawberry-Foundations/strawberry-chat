use std::time::Duration;

use libstrawberry::colors::{BOLD, C_RESET, LIGHT_GREEN, RESET, BLUE, YELLOW, GREEN};
use tokio::time;

use crate::system_core::commands;
use crate::system_core::commands::CommandCategory;
use crate::system_core::permissions::Permissions;
use crate::database::DATABASE;
use crate::global::{LOGGER, STRAWBERRY_ID_API};
use crate::system_core::internals::MessageToClient;
use crate::system_core::server_core::get_senders_by_username_ignore_case;
use crate::utilities::serializer;

#[allow(clippy::too_many_lines)]
pub fn strawberry_id() -> commands::Command {
    async fn logic(ctx: &commands::Context) -> commands::CommandResponse {
        if ctx.args.is_empty() {
            let strawberry_id = DATABASE.get_val_from_user(&ctx.executor.username, "strawberry_id").await.unwrap();
            return Ok(Some(format!("{BOLD}{LIGHT_GREEN}Your current Strawberry ID: {RESET}{strawberry_id}{C_RESET}")));
        }

        let cmd = ctx.args[0].as_str();

        match cmd {
            "reset" | "remove" => {
                DATABASE.update_val(&ctx.executor.username, "strawberry_id", "").await.unwrap();

                let badges = DATABASE.get_val_from_user(&ctx.executor.username, "badges").await.unwrap();

                let new_badges = badges.replace("🍓", "");

                DATABASE.update_val(&ctx.executor.username, "badges", &new_badges).await.unwrap();

                return Ok(Some(format!("{BOLD}{LIGHT_GREEN}Removed Strawberry ID. Rejoin to apply changes{C_RESET}")))
            },
            "link" => {
                let request = reqwest::get(format!("{STRAWBERRY_ID_API}api/request")).await.unwrap();
                let code = if request.status().is_success() {
                    request.text().await.unwrap_or_else(|_| {
                        LOGGER.warning("Couldn't request a login code for Strawberry ID auth");
                        String::new()
                    })
                } else {
                    String::new()
                };

                if code.is_empty() {
                    ctx.tx_channel.send(MessageToClient::SystemMessage {
                        content: format!("{BOLD}{YELLOW}Strawberry ID is currently not available{C_RESET}")
                    }).await.unwrap();
                }

                ctx.tx_channel.send(MessageToClient::SystemMessage {
                    content: format!("Visit {BOLD}{BLUE}{STRAWBERRY_ID_API}de/login/oauth_dialog/stbchat?code={code}{C_RESET} and authorise access")
                }).await.unwrap();

                let ctx_username = ctx.executor.username.clone();

                tokio::spawn(async move {
                    let conn = get_senders_by_username_ignore_case(ctx_username.as_str()).await;

                    let mut interval = time::interval(Duration::from_secs(5));
                    let mut tries = 0;

                    loop {
                        if tries > 5 {
                            for tx in &conn {
                                tx.send(MessageToClient::SystemMessage {
                                    content: format!("{BOLD}{YELLOW}Cancelled Strawberry ID Login{C_RESET}")
                                }).await.unwrap();
                            }
                            break
                        }

                        let response = reqwest::get(format!("{STRAWBERRY_ID_API}api/oauth/callback?code={code}")).await.unwrap();
                        let body = response.text().await.unwrap();

                        if let Ok(data) = serializer(body.as_str())
                            && data["data"]["status"] != "Invalid Code" && data["data"]["status"] != "Not authenticated" {
                                let username = data["data"]["user"]["username"].as_str().unwrap().to_string();
                                let full_name = data["data"]["user"]["full_name"].as_str().unwrap().to_string();

                                for tx in &conn {
                                    tx.send(MessageToClient::SystemMessage {
                                        content: format!("{BOLD}{GREEN}Logged in as {full_name} (@{username}){C_RESET}")
                                    }).await.unwrap_or_else(|_| LOGGER.error(format!("Invalid session of user {ctx_username}. Please check that this user is not logged in with an invalid session.")));

                                    let badges = DATABASE.get_val_from_user(&ctx_username, "badges").await.unwrap();

                                    if badges.contains("🍓") {
                                        break
                                    }

                                    let new_badges = format!("{badges}🍓");

                                    DATABASE.update_val(&ctx_username, "badges", &new_badges).await.unwrap();
                                }

                                DATABASE.update_val(&ctx_username, "strawberry_id", &username).await.unwrap();
                                
                                break
                            }

                        interval.tick().await;
                        tries += 1;
                    }
                });
            }
            _ => {
                ctx.tx_channel.send(MessageToClient::SystemMessage {
                    content: format!("{BOLD}{YELLOW}Invalid subcommand. Usage: /strawberry-id [remove, link]{C_RESET}")
                }).await.unwrap();
            }
        }

        Ok(None)
    }

    commands::Command {
        name: "strawberry-id".to_string(),
        aliases: vec![],
        description: "Set your Strawberry ID".to_string(),
        category: CommandCategory::User,
        permissions: Permissions::Member,
        required_args: 0,
        handler: |ctx| Box::pin(async move {
            logic(&ctx).await
        }),
    }
}