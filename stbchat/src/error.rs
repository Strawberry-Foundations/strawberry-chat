use thiserror::Error;

#[derive(Error, Debug)]
pub enum StrawberryChatError {
    #[error("Packet is too large (max: 65535, found: {0})")]
    PacketTooLarge(usize),
}
