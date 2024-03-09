//! Checks if the core thread is running, stops the server if not

use std::time::Duration;

use tokio::spawn;
use tokio::sync::mpsc::{channel, Receiver};
use tokio::time::sleep;

use crate::CORE_HANDLE;
use crate::global::LOGGER;
use crate::system_core::server_core::core_thread;

pub async fn watchdog_thread(mut rx: Receiver<()>) {
    loop {
        sleep(Duration::from_secs(4)).await;
        
        if rx.try_recv().is_err() {
            LOGGER.warning("Core thread froze/closed, restarting it...");
            CORE_HANDLE.get().unwrap().lock().unwrap().abort();
            
            let (wd_tx, wd_rx) = channel::<()>(1);
            rx = wd_rx;
            *CORE_HANDLE.get().unwrap().lock().unwrap() = spawn(core_thread(wd_tx));
        }
    }
}