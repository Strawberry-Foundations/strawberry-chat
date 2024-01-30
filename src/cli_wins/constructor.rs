#![allow(unused_imports, unused_variables)]

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


use std::fmt::Write;
use stblib::colors::*;

/// * --------- *
/// |    Test    |
///

pub struct ConstructorOptions {
    pub debug_mode: bool,
}

pub struct Constructor {
    pub title: String,
    pub options: ConstructorOptions
}

#[derive(Default)]
pub struct WindowBuilder {
    pub title: String,
    pub label: String,
    pub property_header: String,
    pub property_footer: String,
    pub property_label: String,
}

pub struct Window {
    pub window_builder: WindowBuilder
}

impl Constructor {
    #![allow(clippy::needless_pass_by_value)]
    pub fn new(title: impl ToString, constructor_options: ConstructorOptions) -> Self {
        Self {
            title: title.to_string(),
            options: constructor_options
        }
    }

    pub fn builder(&self) -> WindowBuilder {
        WindowBuilder::new(&self.title)
    }
}

impl WindowBuilder {
    pub fn new(title: impl ToString) -> Self {
        Self {
            title: title.to_string(),
            ..Default::default()
        }
    }

    pub fn label(&self, label: impl ToString) -> Self {
        Self {
            title: self.title.clone(),
            label: label.to_string(),
            property_header: self.property_header.clone(),
            property_footer: self.property_footer.clone(),
            property_label: self.property_label.clone(),
        }
    }

    pub fn build(mut self, ) -> Window {
        let mut header = String::new();
        let mut footer = String::new();
        let mut label = String::new();


        write!(header, " * ").unwrap();

        for _ in 0..(((self.label.len() - self.title.len()) / 2) - 1) {
            write!(header, "-").unwrap();
        }

        write!(header, " {} ", self.title).unwrap();

        let sub_len = usize::from(self.title.len() % 2 == 0);
        let sub_len_2 = usize::from(self.label.len() % 2 != 0);

        if self.label.len() % 2 == 0 {
            for _ in 0..((((self.label.len() - self.title.len()) / 2) - sub_len) - sub_len_2) {
                write!(header, "-").unwrap();
            }
        } else {
            for _ in 0..((((self.label.len() - self.title.len()) / 2) + 1) - sub_len_2) {
                write!(header, "-").unwrap();
            }
        };



        write!(header, " * ").unwrap();

        write!(label, " | ").unwrap();

        for _ in 0..(self.property_header.len() / 2) {
            write!(label, "-").unwrap();
        }

        write!(label, "{}", self.label).unwrap();

        write!(label, " |").unwrap();

        write!(footer, " * ").unwrap();

        for _ in 0..self.label.len() {
            write!(footer, "-").unwrap();
        }

        write!(footer, " * ").unwrap();

        self.property_header = header;
        self.property_footer = footer;
        self.property_label = label;

        Window {
            window_builder: self,
        }
    }
}

impl Window {
    pub fn show(&self,) {
        println!("{}", self.window_builder.property_header);
        println!("{}", self.window_builder.property_label);
        println!("{}", self.window_builder.property_footer);
    }
}

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