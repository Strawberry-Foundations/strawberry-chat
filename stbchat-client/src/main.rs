use tokio::net::TcpStream;

use stbchat::packet::ServerboundPacket;
use stbchat::read_write::write_packet;

#[tokio::main]
async fn main() {
    let mut stream = TcpStream::connect("0.0.0.0:49200").await.unwrap();
    let packet = ServerboundPacket::Authenticate {
        user: "test".to_string(),
        password: "passw0rd".to_string(),
    };
    write_packet(&packet, &mut stream).await.unwrap();
}
