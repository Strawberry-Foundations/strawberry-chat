use crate::error::StrawberryChatError::PacketTooLarge;
use color_eyre::eyre::bail;
use num_traits::FromPrimitive;
use serde::de::DeserializeOwned;
use serde::Serialize;
use std::io;
use std::io::ErrorKind;
use tokio::io::{AsyncReadExt, AsyncWriteExt};

pub async fn read_packet<R: AsyncReadExt + Unpin, P: DeserializeOwned>(
    stream: &mut R,
) -> color_eyre::Result<P> {
    let mut len_buf = [0u8; 2];
    let n = stream.read_exact(&mut len_buf).await?;
    if n == 0 {
        return Err(
            io::Error::new(ErrorKind::ConnectionReset, "Connection was closed by peer").into(),
        );
    }
    let len = u16::from_be_bytes(len_buf) as usize;
    let mut packet_buf = vec![0u8; len];
    let n = stream.read_exact(&mut packet_buf).await?;
    if n == 0 {
        return Err(
            io::Error::new(ErrorKind::ConnectionReset, "Connection was closed by peer").into(),
        );
    }
    let packet = rmp_serde::from_slice(&packet_buf)?;
    Ok(packet)
}

pub async fn write_packet<W: AsyncWriteExt + Unpin, P: Serialize>(
    packet: &P,
    stream: &mut W,
) -> color_eyre::Result<()> {
    let raw_packet = rmp_serde::to_vec_named(&packet)?;
    let packet_size = match u16::from_usize(raw_packet.len()) {
        Some(l) => l,
        None => return Err(PacketTooLarge(raw_packet.len()).into()),
    };
    let mut packet = vec![];
    packet.extend_from_slice(&packet_size.to_be_bytes());
    packet.extend_from_slice(&raw_packet);
    stream.write_all(&packet).await?;
    Ok(())
}
