use std::time::Duration;

use sqlx::Row;
use stblib::colors::{BOLD, C_RESET, RED, LIGHT_GREEN, RESET, BLUE, YELLOW, GREEN};
use tokio::time;

use crate::system_core::commands;
use crate::system_core::commands::CommandCategory;
use crate::system_core::permissions::Permissions;
use crate::database::db::DATABASE;
use crate::global::{LOGGER, STRAWBERRY_ID_API};
use crate::system_core::internals::MessageToClient;
use crate::system_core::server_core::get_senders_by_username_ignore_case;
use crate::utilities::serializer;

#[allow(clippy::too_many_lines)]
pub fn strawberry_id() -> commands::Command {
    async fn logic(ctx: &commands::Context) -> commands::CommandResponse {
        if ctx.args.is_empty() {
            return sqlx::query("SELECT strawberry_id FROM users WHERE username = ?")
                .bind(&ctx.executor.username)
                .fetch_one(&DATABASE.connection)
                .await
                .map_or_else(|_| Err(format!("{BOLD}{RED}Sorry, this user does not exist!{C_RESET}")), |res| {
                    let strawberry_id: String = res.get("strawberry_id");
                    Ok(Some(format!("{BOLD}{LIGHT_GREEN}Your current Strawberry ID: {RESET}{strawberry_id}{C_RESET}")))
            });
        }

        let cmd = ctx.args[0].as_str();

        match cmd {
            "reset" | "remove" => {
                match sqlx::query("UPDATE users SET strawberry_id = '' WHERE username = ?")
                .bind(&ctx.executor.username)
                .execute(&DATABASE.connection)
                .await {
                Ok(..) => ..,
                Err(_) => return Err(format!("{BOLD}{RED}Sorry, this user does not exist!{C_RESET}"))
                };

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

                        if let Ok(data) = serializer(body.as_str()) {
                            if data["data"]["status"] != "Invalid Code" && data["data"]["status"] != "Not authenticated" {
                                let username = data["data"]["user"]["username"].as_str().unwrap().to_string();
                                let full_name = data["data"]["user"]["full_name"].as_str().unwrap().to_string();

                                for tx in &conn {
                                    tx.send(MessageToClient::SystemMessage {
                                        content: format!(
                                            "{BOLD}{GREEN}Logged in as {full_name} (@{username}){C_RESET}"
                                        )
                                    }).await.unwrap();
                                }

                                if sqlx::query("UPDATE users SET strawberry_id = ? WHERE username = ?")
                                    .bind(username)
                                    .bind(&ctx_username)
                                    .execute(&DATABASE.connection)
                                    .await.is_ok() {};
                                
                                break
                            }
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