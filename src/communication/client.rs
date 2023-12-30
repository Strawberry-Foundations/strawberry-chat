use tokio::io::AsyncWriteExt;
use tokio::net::TcpStream;

pub async fn client_handler(mut client: TcpStream) {
    client.write_all(b"hehehe").await.expect("");
}