use libstrawberry::stbchat::object::User;
use tokio::sync::mpsc::{channel, Sender, Receiver};
use crate::system_core::internals::MessageToClient;
use crate::system_core::server_core::{Event, register_hook};

pub struct Hook {
    pub tx: Sender<Event>,
    pub rx: Receiver<Event>,
    pub user: User,
    pub uses: usize,
    pub tx_ctx: Sender<MessageToClient>,

}

impl Hook {
    pub async fn new(user: User, tx_ctx: Sender<MessageToClient>, hook_uses: usize) -> Self {
        let (tx, rx) = channel::<Event>(32);

        let hook = Self {
            tx,
            rx,
            user,
            uses: hook_uses,
            tx_ctx,
        };
        
        register_hook(hook.tx.clone(), hook.user.clone(), hook.uses).await;
        
        hook
    }
}