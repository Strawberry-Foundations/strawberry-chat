#![allow(unused_imports, unused_variables, clippy::wildcard_imports, clippy::needless_pass_by_value)]

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


pub struct ConstructorOptions {
    pub debug_mode: bool,
}

pub struct Constructor {
    pub title: String,
    pub border_color: String,
    pub spacing: usize,
    pub options: ConstructorOptions
}

#[derive(Default)]
pub struct WindowBuilder {
    pub title: String,
    pub label: String,
    pub spacing: usize,
    pub property_header: String,
    pub property_border_color: String,
    pub property_footer: String,
    pub property_label: String,
    pub property_label_color: String,
}

pub struct Window {
    pub window_builder: WindowBuilder
}

impl Constructor {
    #![allow(clippy::needless_pass_by_value)]
    pub fn new(title: impl ToString, border_color: impl ToString, spacing: usize, constructor_options: ConstructorOptions) -> Self {
        Self {
            title: title.to_string(),
            border_color: border_color.to_string(),
            spacing,
            options: constructor_options
        }
    }

    pub fn builder(&self) -> WindowBuilder {
        WindowBuilder::new(
            &self.title,
            &self.border_color,
            self.spacing,
        )
    }
}

impl WindowBuilder {
    pub fn new(title: &impl ToString, border_color: &impl ToString, spacing: usize) -> Self {
        Self {
            title: title.to_string(),
            property_border_color: border_color.to_string(),
            spacing,
            ..Default::default()
        }
    }

    pub fn label(&self, label: impl ToString, color: impl ToString) -> Self {
        Self {
            title: self.title.clone(),
            label: label.to_string(),
            spacing: self.spacing,
            property_header: self.property_header.clone(),
            property_border_color: self.property_border_color.clone(),
            property_footer: self.property_footer.clone(),
            property_label: self.property_label.clone(),
            property_label_color: color.to_string(),
        }
    }

    pub fn build(mut self, ) -> Window {
        let mut header = String::new();
        let mut footer = String::new();
        let mut label = String::new();

        let spacing = " ".repeat(self.spacing);


        write!(header, "{}", self.property_border_color).unwrap();
        write!(header, "{spacing}* ").unwrap();

        for _ in 0..(((self.label.len() - self.title.len()) / 2) - 1) {
            write!(header, "-").unwrap();
        }

        write!(header, " {} ", self.title).unwrap();

        let sub_len = usize::from(self.title.len() % 2 == 0);
        let sub_len_2 = usize::from(self.label.len() % 2 != 0);
        let sub_len_3 = usize::from(self.title.len() < self.label.len());


        if self.label.len() % 2 == 0 {
            for _ in 0..((((self.label.len() - self.title.len()) / 2) - sub_len) - sub_len_2) {
                write!(header, "-").unwrap();
            }
        } else {
            for _ in 0..(((((self.label.len() - self.title.len()) / 2) + 1) - sub_len_2) - sub_len_3) {
                write!(header, "-").unwrap();
            }
        };

        write!(header, " * ").unwrap();

        write!(label, "{spacing}| ").unwrap();

        for _ in 0..(self.property_header.len() / 2) {
            write!(label, "-").unwrap();
        }

        write!(label, "{}{}{C_RESET}{}", self.property_label_color, self.label, self.property_border_color).unwrap();

        write!(label, " |").unwrap();

        write!(footer, "{spacing}* ").unwrap();

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