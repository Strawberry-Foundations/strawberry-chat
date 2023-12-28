//! Contains the structure of the packets sent between client and server

use crate::user::User;
use serde::{Deserialize, Serialize};

/// A packet sent from the server to the client (S2C)
#[derive(Serialize, Deserialize)]
#[serde(tag = "packet_type")]
pub enum ClientboundPacket {
    Disconnect { reason: String },

    // LOGIN
    LoginSuccess,
    LoginFail,

    // POST-LOGIN
    UserMessageReceive { author: User, content: String },
    SystemMessageReceive { raw: String },
}

/// A packet sent from the client to the server (C2S)
#[derive(Serialize, Deserialize)]
#[serde(tag = "packet_type")]
pub enum ServerboundPacket {
    // LOGIN
    /// Packet sent to authenticate
    /// Server will respond with LoginSuccess or LoginFail
    Authenticate {
        user: String,
        password: String,
    },
    Register {
        name: String,
        password: String,
        color: NameColor,
    },

    // POST-LOGIN
    MessageSend {
        content: String,
    },
    CommandRun {
        command: String,
        args: Vec<String>,
    },
}

#[derive(Serialize, Deserialize)]
#[repr(u8)]
pub enum NameColor {
    Red,
    Blue,
    Green,
    Orange,
    Purple,
}
