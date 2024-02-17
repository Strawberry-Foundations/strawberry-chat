use crate::system_core::commands;
use crate::system_core::commands::CommandCategory;

pub fn panic_command() -> commands::Command {
    async fn logic(_: &commands::Context) -> commands::CommandResponse {
        panic!();
    }

    commands::Command {
        name: "panic".to_string(),
        aliases: vec![],
        description: "Panics the core thread - DEBUG ONLY".to_string(),
        category: CommandCategory::Etc,
        handler: |ctx| Box::pin(async move {
            logic(&ctx).await
        }),
    }
}