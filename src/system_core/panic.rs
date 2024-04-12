use core::panic::PanicInfo;
use crate::global::LOGGER;

pub fn panic_handler(info: &PanicInfo) {
    let location = info.location()
        .map_or_else(
            || String::from("an unknown file"),
            |location| format!("file '{}' at line {}", location.file(), location.line())
        );

    LOGGER.critical(
        format!(
            "Core thread panicked in {location}",
        )
    );
}