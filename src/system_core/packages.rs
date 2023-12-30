use crate::system_core::types::PackageTypes;

pub struct MessageStruct {
    content: String
}

pub struct SystemMessage {
    message_type: PackageTypes,
    message: MessageStruct,
}

impl SystemMessage {
    pub const fn new() -> Self {
        Self {
            message_type: PackageTypes::SystemMessage,
            message: MessageStruct {
                content: String::new()
            }
        }
    }

    pub fn write(&self, message: impl ToString) -> String {
        message.to_string()
    }
}