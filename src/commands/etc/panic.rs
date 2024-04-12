use crate::system_core::commands;
use crate::system_core::commands::CommandCategory;
use crate::system_core::permissions::Permissions;

pub fn panic_command() -> commands::Command {
    fn logic(_: &commands::Context) -> commands::CommandResponse {
        panic!("explicit panic executed by command");
    }

    commands::Command {
        name: "panic".to_string(),
        aliases: vec![],
        description: "Panics the core thread - DEBUG ONLY".to_string(),
        category: CommandCategory::Etc,
        permissions: Permissions::Admin,
        handler: |ctx| Box::pin(async move {
            logic(&ctx)
        }),
    }
}