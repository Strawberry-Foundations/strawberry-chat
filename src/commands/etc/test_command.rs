use crate::system_core::commands;

pub fn example_command() -> commands::Command {
    fn logic(ctx: &commands::Context) -> Result<String, String> {
        Ok({
            format!("Username: {}", ctx.executor.username);
            format!("Args: {:?}", ctx.args)
        })
    }

    commands::Command {
        name: "test".to_string(),
        description: "Example command".to_string(),
        handler: |ctx| Box::pin(async move {
            logic(&ctx)
        }),
    }
}