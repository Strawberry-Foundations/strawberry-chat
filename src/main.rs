#![warn(clippy::all, clippy::nursery, clippy::pedantic)]
#![allow(clippy::module_name_repetitions, clippy::should_implement_trait, clippy::struct_excessive_bools)]
#![allow(dead_code)]

use crate::global::CONFIG;

mod config;
mod utilities;
mod global;

fn main() {
    println!("{}:{}", CONFIG.server.address, CONFIG.server.port);
}
