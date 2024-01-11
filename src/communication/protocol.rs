pub struct BlockedWords<'a> {
    pub blacklisted_words: Vec<&'a str>,
    pub content_block: Vec<&'a str>,
}

pub struct MessageVerification {
    pub blocked_words: BlockedWords<'static>,
}

impl MessageVerification {
    pub fn new() -> Self {
        Self {
            blocked_words: BlockedWords {
                blacklisted_words: vec![],
                content_block: vec!["[#<keepalive.event.sent>]"],
            }
        }
    }
}