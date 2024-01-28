#![allow(unused_imports)]
#![allow(unused_variables)]

//! # Command-Line Windows
//! Command-Line Windows is a library to create nice but simple little command line windows.
//! **WARNING**: This is experimental
//! This might get moved to stblib in the future

use stblib::colors::*;

pub fn print_window(txt: &str) {
    let margin = if txt.len() % 2 == 0 { "  " } else { " " };

    print!(" *");
    for txt in 0..(txt.len() + 5) {
        print!("-");
    }
    print!("*");
    println!();
    print!(" |");
    for txt in 0..(txt.len() / 2) {
        print!("{margin}");
    }
    print!("{txt}");
    for txt in 0..(txt.len() / 2) {
        print!("{margin}");
    }
    print!("|");
    println!();
    print!("*");
    for txt in 0..(txt.len() + 5) {
        print!("-");
    }
    print!("*");
    println!();
}