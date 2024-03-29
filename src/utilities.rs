use std::fs;
use std::io::{self, Write};

use stblib::colors::{BLUE, BOLD, CYAN, GREEN, MAGENTA, RED, RESET, YELLOW};

use crate::global::{CONFIG, LOGGER};

pub fn open_config(config_path: &str) -> String {
    fs::read_to_string(config_path).unwrap_or_else(|_| {
        LOGGER.panic("Could not open your configuration");
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

pub fn runtime_all_addresses() -> String {
    if CONFIG.server.address == "0.0.0.0" {
        " (All addresses)".to_string()
    }
    else {
        String::new()
    }
}

pub fn delete_last_line() {
    print!("\x1b[1A");
    print!("\x1b[2K");
    io::stdout().flush().unwrap();
}

pub fn role_color_parser(color: &str) -> String {
    match color {
        "red" => RED.to_string(),
        "green" => GREEN.to_string(),
        "yellow" => YELLOW.to_string(),
        "blue" => BLUE.to_string(),
        "magenta" => MAGENTA.to_string(),
        "cyan" => CYAN.to_string(),

        "bred" => format!("{RED}{BOLD}"),
        "bgreen" => format!("{GREEN}{BOLD}"),
        "byellow" => format!("{YELLOW}{BOLD}"),
        "bblue" => format!("{BLUE}{BOLD}"),
        "bmagenta" => format!("{MAGENTA}{BOLD}"),
        "bcyan" => format!("{CYAN}{BOLD}"),
        _ => String::new()
    }
}

pub fn is_valid_username(username: &str, allowed_characters: &str) -> bool {
    for c in username.chars() {
        if !allowed_characters.contains(c) {
            return false;
        }
    }
    true
}
