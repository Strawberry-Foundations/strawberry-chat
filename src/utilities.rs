use std::fs;
use stblib::colors::{CYAN, GREEN, RED, RESET};
use crate::global::{CONFIG, LOGGER};

pub fn open_config(config_path: &str) -> String {
    fs::read_to_string(config_path).unwrap_or_else(|_| {
        LOGGER.panic("Could not open your configuration");
        unreachable!()
    })
}

pub fn is_feature_enabled(feature_state: bool) -> String {
    if feature_state {
        format!("{GREEN}enabled ")
    }
    else {
        format!("{RED}disabled")
    }
}

pub fn get_ratelimit_timeout(feat_enabled: bool) -> String {
    let rlm = CONFIG.networking.ratelimit_timeout.to_string();
    if feat_enabled {
        match rlm.len() {
            1 => format!("{RESET}({CYAN}{rlm}s{RESET})    "),
            2 => format!("{RESET}({CYAN}{rlm}s{RESET})   "),
            3 => format!("{RESET}({CYAN}{rlm}s{RESET})  "),
            4 => format!("{RESET}({CYAN}{rlm}s{RESET}) "),
            5 => format!("{RESET}({CYAN}{rlm}s{RESET})"),
            _ => "        ".to_string(),
        }
    }
    else {
        "        ".to_string()
    }
}