use std::fs;
use std::io::{self, Write};
use stblib::colors::{BLUE, BOLD, C_RESET, CYAN, GRAY, GREEN, MAGENTA, RED, RESET, YELLOW};

use crate::system_core::config::DEFAULT_CONFIG;
use crate::system_core::status::Status;
use crate::global::{CONFIG, LOGGER};
use crate::constants::badges::{
    BERRYJUICE_BADGE, BOT_BADGE, COOL_BADGE, CROWN_BADGE, EVIL_BADGE, FLAME_BADGE,
    KINDNESS_BADGE, MACHER_BADGE, NEWBIE_BADGE, OG_BADGE, STBCHAT_PLUS_USER, STRAWBERRY_BADGE,
    SUPPORTER_BADGE, TROLL_BADGE
};

pub fn open_config(config_path: &str) -> String {
    fs::read_to_string(config_path).unwrap_or_else(|_| {
        LOGGER.error("Could not open your configuration");
        LOGGER.info("Trying to create a new config...");

        fs::write(config_path, DEFAULT_CONFIG).unwrap();

        fs::read_to_string(config_path).unwrap()
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
    let ratelimit_timeout = CONFIG.networking.ratelimit_timeout.to_string();
    if feat_enabled {
        match ratelimit_timeout.len() {
            1 => format!("{RESET}({CYAN}{ratelimit_timeout}s{RESET})    "),
            2 => format!("{RESET}({CYAN}{ratelimit_timeout}s{RESET})   "),
            3 => format!("{RESET}({CYAN}{ratelimit_timeout}s{RESET})  "),
            4 => format!("{RESET}({CYAN}{ratelimit_timeout}s{RESET}) "),
            5 => format!("{RESET}({CYAN}{ratelimit_timeout}s{RESET})"),
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

pub fn create_badge_list(row: &str) -> String {
    if row.is_empty() {
        return "This user doesn't have any badges yet".to_string();
    }

    let badge_pairs = [
        ('👑', CROWN_BADGE),
        ('😎', COOL_BADGE),
        ('🔥', FLAME_BADGE),
        ('🫐', BERRYJUICE_BADGE),
        ('🤖', BOT_BADGE),
        ('💪', MACHER_BADGE),
        ('👍', KINDNESS_BADGE),
        ('🤡', TROLL_BADGE),
        ('😈', EVIL_BADGE),
        ('🤝', SUPPORTER_BADGE),
        ('👋', NEWBIE_BADGE),
        ('😌', OG_BADGE),
        ('🍓', STRAWBERRY_BADGE),
        ('💫', STBCHAT_PLUS_USER),
    ];

    badge_pairs
        .iter()
        .filter(|(emoji, _)| row.contains(*emoji))
        .fold(String::new(), |mut acc, (_, badge)| {
            acc.push_str("\n        ");
            acc.push_str(badge);
            acc
        })
}

pub fn parse_user_status(status: Status) -> (String, String) {
    match status {
        Status::Online => (format!("{GREEN}🟢{C_RESET}"), format!("{GREEN}Online (🟢){C_RESET}")),
        Status::Afk => (format!("{YELLOW}🌙{C_RESET}"), format!("{YELLOW}Afk (🌙){C_RESET}")),
        Status::DoNotDisturb => (format!("{RED}🔴{C_RESET}"), format!("{RED}Do not disturb (🔴){C_RESET}")),
        Status::Offline => (format!("{GRAY}{BOLD}〇{C_RESET}"), format!("{GRAY}{BOLD}Offline (〇){C_RESET}"))
    }
}

pub fn serializer(text: &str) -> Result<serde_json::Value, serde_json::Error> {
    let serializer = serde_json::from_str(text)?;
    Ok(serializer)
}