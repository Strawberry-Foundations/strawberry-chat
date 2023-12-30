use std::fs;
use crate::global::LOGGER;

pub fn open_config(config_path: &str) -> String {
    fs::read_to_string(config_path).unwrap_or_else(|_| {
        LOGGER.panic("Could not open your configuration");
        unreachable!()
    })
}