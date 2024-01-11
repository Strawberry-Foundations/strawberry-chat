use crate::system_core::commands;
// use crate::system_core::message::MessageToClient;

pub fn example_command() -> commands::Command {
    fn logic(ctx: &commands::Context) -> Result<Option<String>, String> {
        // ctx.tx_channel.send(MessageToClient::SystemMessage { content: "Hello".into() }).unwrap();
        Ok(Some(format!("\n  Username: {}\n  Args: {:?}", ctx.executor.username, ctx.args)))
    }

    commands::Command {
        name: "test".to_string(),
        description: "Example command".to_string(),
        handler: |ctx| Box::pin(async move {
            logic(&ctx)
        }),
    }
}