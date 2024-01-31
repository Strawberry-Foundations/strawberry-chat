use stblib::colors::{BLUE, BOLD, CYAN, GREEN, MAGENTA, RED, RESET, UNDERLINE, WHITE, YELLOW};
use chrono::{Utc, Local, Datelike, Timelike};

pub struct StbString {
    pub string: String
}

impl StbString {
    pub fn from_str(string: impl ToString) -> Self {
        Self {
            string: string.to_string(),
        }
    }

    pub fn apply_htpf(mut self,) -> Self {
        self.string = self.string
            .replace("#red", RED)
            .replace("#green", GREEN)
            .replace("#yellow", YELLOW)
            .replace("#blue", BLUE)
            .replace("#magenta", MAGENTA)
            .replace("#cyan", CYAN)
            .replace("#white", WHITE)
            .replace("#reset", RESET)
            .replace("#bold", BOLD)
            .replace("#underline", UNDERLINE)
            .replace("#today", &Utc::today().format("%Y-%m-%d").to_string())
            .replace("#curtime", &Local::now().format("%H:%M").to_string())
            .replace("#month", &Utc::today().format("%m").to_string())
            .replace("#fullmonth", &Local::now().format("%h").to_string())
            .replace("#ftoday", &Local::now().format("%A, %d. %h %Y").to_string())
            .replace("#tomorrow", &(Utc::today() + chrono::Duration::days(1)).format("%Y-%m-%d").to_string())
            .replace("#ftomorrow", &(Local::now() + chrono::Duration::days(1)).format("%A, %d. %h %Y").to_string());

        ;

        self
    }

    #[allow(clippy::inherent_to_string)]
    pub fn to_string(&self) -> String {
        self.string.clone()
    }
}