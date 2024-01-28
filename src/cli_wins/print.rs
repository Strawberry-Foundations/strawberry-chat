#![allow(unused_imports)]
#![allow(unused_variables)]

use stblib::colors::*;

// warning this is experimental
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