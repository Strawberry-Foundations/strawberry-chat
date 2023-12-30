use std::env;
use std::path::{Path, PathBuf};
use lazy_static::lazy_static;

use crate::config::GlobalConfig;
use stblib::logging::Logger;

lazy_static! {
    pub static ref LOGGER: Logger = Logger::new(
        stblib::logging::featureset::FeatureSet::new(),
        stblib::logging::formats::strawberry_chat_fmt()
    );

    pub static ref CONFIG: GlobalConfig = {
        let exe_path = env::current_exe().unwrap_or_else(|_| {
            LOGGER.panic("Could not get your Strawberry Chat Runtime Executable");
            unreachable!()
        });

        let exe_dir = exe_path.parent().unwrap_or_else(|| {
            LOGGER.panic("Could not get directory of your Strawberry Chat Runtime Executable");
            unreachable!()
        });

        let exe_dir_str = PathBuf::from(exe_dir).display().to_string();

        let mut config_path = format!("{exe_dir_str}/config.yml");

        if !Path::new(&config_path).exists() {
            config_path = String::from("./config.yml")
        }

        GlobalConfig::new(config_path)
    };
}