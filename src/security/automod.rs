pub struct BlockedWords<'a> {
    pub blacklisted_words: Vec<&'a str>,
    pub content_block: Vec<&'a str>,
}

pub struct MessageVerification {
    pub blocked_words: BlockedWords<'static>,
}

#[derive(PartialEq, Eq)]
pub enum MessageAction {
    Allow,
    Hide,
    Kick
}

impl MessageVerification {
    pub fn check(&self, content: &impl ToString) -> MessageAction {
        let content = content.to_string();

        if self.blocked_words.blacklisted_words.iter().any(|w| content.contains(w)) {
            return MessageAction::Kick;
        }
        if self.blocked_words.content_block.iter().any(|w| content.contains(w)) {
            return MessageAction::Hide;
        }

        if content.trim().is_empty() {
            return MessageAction::Hide;
        }

        MessageAction::Allow
    }
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