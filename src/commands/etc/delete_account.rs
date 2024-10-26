use tokio::spawn;

use stblib::utilities::escape_ansi;
use stblib::colors::{BOLD, C_RESET, GREEN, RED, YELLOW};

use crate::system_core::commands;
use crate::system_core::commands::CommandCategory;
use crate::system_core::hooks::Hook;
use crate::system_core::internals::MessageToClient;
use crate::system_core::permissions::Permissions;
use crate::system_core::server_core::Event;
use crate::database::DATABASE;

pub fn delete_account() -> commands::Command {
    async fn logic(ctx: &commands::Context) -> commands::CommandResponse {
        ctx.tx_channel.send(MessageToClient::SystemMessage {
            content: format!("{YELLOW}{BOLD}Are you sure you want to delete your user account? This action is irreversible!!{C_RESET}")
        }).await.unwrap();

        let mut hook = Hook::new(ctx.executor.clone(), ctx.tx_channel.clone(), 1).await;

        spawn(async move {
            if let Some(Event::UserMessage { content, .. }) = hook.rx.recv().await {
                // First time for confirming account deletion
                if escape_ansi(&content).eq_ignore_ascii_case("yes") {
                    hook.tx_ctx.send(MessageToClient::SystemMessage {
                        content: format!("{RED}{BOLD}THIS IS YOUR VERY LAST WARNING! This action is irreversible!! ARE YOU SURE?{C_RESET}")
                    }).await.unwrap();

                    let mut hook = Hook::new(hook.user, hook.tx_ctx, hook.uses).await;

                    if let Some(Event::UserMessage { content, ..}) = hook.rx.recv().await {
                        // Second time for confirming account deletion
                        if escape_ansi(&content).eq_ignore_ascii_case("yes") {
                            hook.tx_ctx.send(MessageToClient::SystemMessage {
                                content: format!("{YELLOW}{BOLD}Enter your username to confirm the deletion of your account:{C_RESET}")
                            }).await.unwrap();

                            let mut hook = Hook::new(hook.user, hook.tx_ctx, hook.uses).await;

                            if let Some(Event::UserMessage { author, content}) = hook.rx.recv().await {
                                // Third time for confirming account deletion
                                if escape_ansi(&content) == author.username {
                                    hook.tx_ctx.send(MessageToClient::SystemMessage {
                                        content: format!("{YELLOW}{BOLD}Now, enter your password to finally confirm your account deletion:{C_RESET}")
                                    }).await.unwrap();

                                    let mut hook = Hook::new(hook.user, hook.tx_ctx, hook.uses).await;

                                    if let Some(Event::UserMessage { author, content}) = hook.rx.recv().await {
                                        // Last time for confirming account deletion
                                        let (_, result) = DATABASE.check_credentials(&author.username, &content).await;

                                        if result {
                                            hook.tx_ctx.send(MessageToClient::SystemMessage {
                                                content: format!("{YELLOW}{BOLD}Deleting your user account...{C_RESET}")
                                            }).await.unwrap();

                                            DATABASE.delete_user(author.username).await;

                                            hook.tx_ctx.send(MessageToClient::SystemMessage {
                                                content: format!("{GREEN}{BOLD}Deleted. Goodbye!{C_RESET}")
                                            }).await.unwrap();

                                        } else {
                                            hook.tx_ctx.send(MessageToClient::SystemMessage {
                                                content: format!("{YELLOW}{BOLD}Deletion of your account has been canceled...{C_RESET}")
                                            }).await.unwrap();
                                        }
                                    }
                                } else {
                                    hook.tx_ctx.send(MessageToClient::SystemMessage {
                                        content: format!("{YELLOW}{BOLD}Deletion of your account has been canceled...{C_RESET}")
                                    }).await.unwrap();
                                }
                            }
                        } else {
                            hook.tx_ctx.send(MessageToClient::SystemMessage {
                                content: format!("{YELLOW}{BOLD}Deletion of your account has been canceled...{C_RESET}")
                            }).await.unwrap();
                        }
                    }
                } else {
                    hook.tx_ctx.send(MessageToClient::SystemMessage {
                        content: format!("{YELLOW}{BOLD}Deletion of your account has been canceled...{C_RESET}")
                    }).await.unwrap();
                }
            }
        });
        
        Ok(None)
    }

    commands::Command {
        name: "deleteaccount".to_string(),
        aliases: vec!["delaccount"],
        description: "Delete your account on this server".to_string(),
        category: CommandCategory::Etc,
        permissions: Permissions::Member,
        required_args: 0,
        handler: |ctx| Box::pin(async move {
            logic(&ctx).await
        }),
    }
}