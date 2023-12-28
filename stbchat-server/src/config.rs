use lazy_static::lazy_static;
use serde::Deserialize;

lazy_static! {
    pub static ref CONFIG: Config =
        { toml::from_str(include_str!("StrawberryChat.toml")).expect("Failed to parse config") };
}

#[derive(Deserialize)]
pub struct Config {
    pub bind: BindOpts,
}

#[derive(Deserialize)]
pub struct BindOpts {
    pub addr: String,
    pub port: u16,
}
