//! Handles messages from the client handler threads

use std::time::Duration;

use log::info;
use tokio::sync::mpsc::UnboundedReceiver;
use tokio::time::sleep;

use stbchat::user::User;

use crate::connection::Connection;
use crate::message::{MessageFromClient, MessageToClient};

#[derive(Debug)]
enum Event {
    UserMessage { user: User, content: String },
    RemoveConnection { idx: usize },
}

fn get_events(conns: &mut [Connection]) -> Vec<Event> {
    let mut events = vec![];
    for (i, conn) in conns.iter_mut().enumerate() {
        if let Ok(msg) = conn.from_client.try_recv() {
            match msg {
                MessageFromClient::Authenticated { user } => {
                    conn.auth(user);
                }
                MessageFromClient::SentMessage { content } => {
                    let user = match conn.get_user() {
                        Some(u) => u.clone(),
                        None => continue,
                    };
                    events.push(Event::UserMessage { user, content });
                }
                MessageFromClient::RanCommand { .. } => {}
                MessageFromClient::RemoveMe => {
                    events.push(Event::RemoveConnection { idx: i });
                }
            }
        }
    }
    events
}

pub async fn messages_handler(mut conns_recv: UnboundedReceiver<Connection>) {
    let mut conns = vec![];
    loop {
        while let Ok(conn) = conns_recv.try_recv() {
            conns.push(conn);
        }
        let events = get_events(&mut conns);
        for event in events {
            match event {
                Event::UserMessage { user, content } => {
                    info!("{} sent {content}", user.name);
                    for c in conns.iter_mut().filter(|c| c.is_auth()) {
                        c.to_client
                            .send(MessageToClient::ReceiveUserMessage {
                                user: user.clone(),
                                content: content.clone(),
                            })
                            .expect("Failed to send message through ");
                    }
                }
                Event::RemoveConnection { idx } => {
                    conns.remove(idx);
                }
            }
        }
        sleep(Duration::from_millis(100)).await;
    }
}
