use std::env;
use std::path::{Path, PathBuf};
use lazy_static::lazy_static;

use crate::config::Config;

lazy_static! {
    pub static ref CONFIG: Config = {
        let exe_path = env::current_exe().unwrap_or_else(|err| {
            todo!(); // stblib logging
            std::process::exit(1);
        });

        let exe_dir = exe_path.parent().unwrap_or_else(|err| {
            todo!(); // stblib logging
            std::process::exit(1);
        });

        let exe_dir_str = PathBuf::from(exe_dir).display().to_string();

        let mut config_path = format!("{exe_dir_str}/config.yml");

        if !Path::new(&config_path).exists() {
            config_path = String::from("./config.yml")
        }

        Config::new(config_path)
    };
}