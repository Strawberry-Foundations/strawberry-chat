use std::time::Duration;

use tokio::io::{stdin, AsyncReadExt};
use tokio::net::TcpStream;
use tokio::time::sleep;

use stbchat::packet::{ClientboundPacket, ServerboundPacket};
use stbchat::read_write::{read_packet, write_packet};

#[tokio::main]
async fn main() {
    let mut stream = TcpStream::connect("0.0.0.0:49200").await.unwrap();
    let mut buf = [0u8; 255];
    println!("Username?");
    let n = stdin().read(&mut buf).await.unwrap();
    let packet_auth = ServerboundPacket::Authenticate {
        user: String::from_utf8_lossy(&buf[..n]).trim().to_string(),
        password: "passw0rd".to_string(),
    };
    write_packet(&packet_auth, &mut stream).await.unwrap();
    println!("wrote packet");
    sleep(Duration::from_secs(5)).await;

    let packet_msg = ServerboundPacket::MessageSend {
        content: "Hello!".to_string(),
    };
    write_packet(&packet_msg, &mut stream).await.unwrap();
    loop {
        let packet: ClientboundPacket = read_packet(&mut stream).await.unwrap();
        match packet {
            ClientboundPacket::Disconnect { reason } => {
                println!("You were disconnected: {reason}");
            }
            ClientboundPacket::UserMessageReceive { author, content } => {
                println!("{} ({}): {content}", author.name, author.nick);
            }
            ClientboundPacket::SystemMessageReceive { raw } => {
                println!("{raw}");
            }
            _ => {}
        }
    }
}
