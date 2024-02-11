use thiserror::Error;

#[derive(Error, Debug)]
pub enum StbChatError {
    #[error("Packet too large. SIZE={0} MAX=65535")]
    PacketTooLarge(usize),
}