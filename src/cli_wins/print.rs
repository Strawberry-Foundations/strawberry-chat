#![allow(unused_imports)]
#![allow(unused_variables)]

//! # Command-Line Windows
//! Command-Line Windows is a library to create nice but simple little command line windows.
//! **WARNING**: This is experimental
//! This might get moved to stblib in the future
//!
//! This could look like this:
//! ```
//! * ------------ Hello World ------------ *
//! | -> Hey! Whats up?                     |
//! | * This is just a test.                |
//! * ------------------------------------- *
//! ```


use stblib::colors::*;

/// * --------- *
/// |    Test    |
///

pub fn print_window(txt: &str) {
    let margin = if txt.len() % 2 == 0 { "  " } else { " " };

    println!("\
--- CLIWins 0.1.0 Debug Information ---
Text Length: {}
Margin Length: {}
    ", txt.len(), margin.len()
    );

    print!(" * ");
    for txt in 0..(txt.len()) {
        print!("-");
    }
    print!(" *");


    println!();
    print!(" | ");

    /* for txt in 0..(txt.len() / 2) {
        print!("{margin}");
    } */

    print!("{txt}");

    for txt in 0..(txt.len() / 2) {
        print!("{margin}");
    }
    print!(" |");
    println!();
    print!("*");
    for txt in 0..(txt.len() + 5) {
        print!("-");
    }
    print!("*");
    println!();
}