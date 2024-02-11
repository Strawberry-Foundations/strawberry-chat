use std::{env::args, io::{stdin, Read}, process::exit, thread::park, time::Duration};

use stbchat::{net::{IncomingPacketStream, OutgoingPacketStream}, packet::{ClientboundPacket, MessageStruct, ServerboundPacket}};
use tokio::{io::{split, ReadHalf, WriteHalf}, net::TcpStream, select, spawn, time::sleep};

async fn s2c(mut r_server: IncomingPacketStream<ReadHalf<TcpStream>>) {
    loop {
        match r_server.read::<ClientboundPacket>().await {
            Ok(ClientboundPacket::SystemMessage { message }) => println!("[sys] {}", message.content),
            Ok(ClientboundPacket::UserMessage { author, message }) => println!("({}) {}", author.username, message.content),
            Err(_) => break,
            _ => {}
        }
    }
}

async fn c2s(mut w_server: OutgoingPacketStream<WriteHalf<TcpStream>>) {
    loop {
        let mut text = [0u8; 1024];
        let n = stdin().read(&mut text).unwrap();
        w_server.write(
            ServerboundPacket::Message {
                message: MessageStruct::new(String::from_utf8_lossy(&text[..n]))
            }
        ).await.expect("Failed to write packet");
    }
}

#[tokio::main]
async fn main() {
    println!("NOTE: This client is for testing only and may have bugs");
    let addr = args().nth(1).unwrap();
    let stream = TcpStream::connect(addr).await.unwrap();
    let (r_server, w_server) = split(stream);
    let r_server = IncomingPacketStream::wrap(r_server);
    let mut w_server = OutgoingPacketStream::wrap(w_server);
    let s2c = spawn(s2c(r_server));
    sleep(Duration::from_millis(50)).await;
    println!("Username:");
    let mut username = [0u8; 1024];
    let n_username = stdin().read(&mut username).unwrap();
    println!("Password:");
    let mut password = [0u8; 1024];
    let n_password = stdin().read(&mut password).unwrap();
    w_server.write(
        ServerboundPacket::Login {
            username: String::from_utf8_lossy(&username[..n_username]).trim().to_string(),
            password: String::from_utf8_lossy(&password[..n_password]).trim().to_string(),
        }
    ).await.expect("Failed to write packet");

    let c2s = spawn(c2s(w_server));
    select! {
        _ = s2c => {exit(0)},
        _ = c2s => {exit(0)}
    }
}
