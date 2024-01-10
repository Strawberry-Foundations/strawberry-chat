use crate::system_core::commands;

pub fn example_command() -> commands::Command {
    fn logic(ctx: &commands::Context) -> Result<String, String> {
        Ok(format!("\n  Username: {}\n  Args: {:?}", ctx.executor.username, ctx.args))
    }

    commands::Command {
        name: "test".to_string(),
        description: "Example command".to_string(),
        handler: |ctx| Box::pin(async move {
            logic(&ctx)
        }),
    }
}