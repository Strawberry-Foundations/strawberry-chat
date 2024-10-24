use std::panic::PanicHookInfo;
use crate::global::LOGGER;

pub fn panic_handler(info: &PanicHookInfo) {
    let location = info.location()
        .map_or_else(
            || String::from("an unknown file"),
            |location| format!("file '{}' at line {}", location.file(), location.line())
        );

    let payload = info.payload()
        .downcast_ref::<&str>()
        .map_or_else(
            String::new,
            |s| format!(": {s:?} "));


        LOGGER.panic(format!("Core thread panicked in {location}{payload}")
    );
}