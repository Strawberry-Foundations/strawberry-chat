pub fn log_parser(log_message: &str, params: &[&dyn std::fmt::Display]) -> String {
    let has_placeholders = log_message.contains('%');
    if has_placeholders {
        let mut formatted_message = log_message.to_string();

        for param in params {
            if let Some(index) = formatted_message.find("%s") {
                formatted_message.replace_range(index..(index + 2), &param.to_string());
            }
            else if let Some(index) = formatted_message.find("%d") {
                if let Ok(value) = param.to_string().parse::<i64>() {
                    formatted_message.replace_range(index..(index + 2), &value.to_string());
                }
            }
        }
        formatted_message.to_string()
    } else {
        log_message.to_string()
    }
}