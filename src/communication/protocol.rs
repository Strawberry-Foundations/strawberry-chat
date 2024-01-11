use serde::de::DeserializeOwned;
use tokio::io::{AsyncRead, AsyncReadExt};

pub struct BlockedWords<'a> {
    pub blacklisted_words: Vec<&'a str>,
    pub content_block: Vec<&'a str>,
}

pub struct MessageVerification {
    pub blocked_words: BlockedWords<'static>,
}

pub struct JsonStreamDeserializer<R: AsyncRead + Unpin> {
    reader: R
}


impl MessageVerification {
    pub fn new() -> Self {
        Self {
            blocked_words: BlockedWords {
                blacklisted_words: vec!["gullideckel"],
                content_block: vec!["[#<keepalive.event.sent>]"],
            }
        }
    }
}

impl<R: AsyncRead + Unpin + Send> JsonStreamDeserializer<R> {
    pub const fn from_read(reader: R) -> Self {
        Self { reader }
    }

    pub async fn next<T: DeserializeOwned + Send>(&mut self) -> eyre::Result<T> {
        let mut bytes = vec![];

        let mut wraps = 0u32;
        let mut in_string = false;
        let mut escape = false;
        loop {
            let byte = self.reader.read_u8().await?;
            if byte != b'{' && wraps == 0 {
                continue;
            }
            match byte {
                b'{' => {
                    if !in_string {
                        wraps += 1;
                    }
                },
                b'}' => {
                    wraps -= 1;
                    if wraps == 0 {
                        bytes.push(byte);
                        break;
                    }
                },
                b'\\' => {
                    escape = true;
                },
                b'"' => {
                    if escape {
                        escape = false;
                    } else {
                        in_string ^= true;
                    }
                }
                _ => {}
            }
            bytes.push(byte);
        }
        let string = String::from_utf8(bytes)?;
        // dbg!(&string);
        Ok(serde_json::from_str(&string)?)
    }
}