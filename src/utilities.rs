use std::fs;

pub fn open_config(config_path: &str) -> String {
    fs::read_to_string(config_path).unwrap_or_else(|err| {
        todo!(); // stblib logging
        std::process::exit(1);
    })
}