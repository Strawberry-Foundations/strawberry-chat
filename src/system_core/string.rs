use stblib::colors::{BACK_MAGENTA, BLUE, BOLD, C_RESET, CYAN, GREEN, MAGENTA, RED, RESET, UNDERLINE, WHITE, YELLOW};
use chrono::{Utc, Local};
use crate::system_core::server_core::get_online_users;

pub struct StbString {
    pub string: String
}

impl StbString {
    #[allow(clippy::needless_pass_by_value)]
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
            .replace("#today", &Utc::now().format("%Y-%m-%d").to_string())
            .replace("#curtime", &Local::now().format("%H:%M").to_string())
            .replace("#month", &Utc::now().format("%m").to_string())
            .replace("#fullmonth", &Local::now().format("%h").to_string())
            .replace("#ftoday", &Local::now().format("%A, %d. %h %Y").to_string())
            .replace("#tomorrow", &(Utc::now() + chrono::Duration::days(1)).format("%Y-%m-%d").to_string())
            .replace("#ftomorrow", &(Local::now() + chrono::Duration::days(1)).format("%A, %d. %h %Y").to_string());

        self
    }

    #[allow(clippy::needless_collect)]
    pub async fn check_for_mention(mut self) -> Self {
        let string_lower = self.string.to_lowercase();
        let msg_split = string_lower.split(' ').collect::<Vec<&str>>();

        for user in &get_online_users().await {
            if msg_split.contains(&&*format!("@{}", user.username.to_lowercase())) {
                self.string = self.string
                    .replace(&format!("@{}", user.username.to_lowercase()), &format!("{BACK_MAGENTA}{BOLD}@{}{C_RESET}", user.nickname))
                    .replace(&format!("@{}", user.username), &format!("{BACK_MAGENTA}{BOLD}@{}{C_RESET}", user.nickname));
            }
        }
        self
    }

    pub fn escape_htpf(mut self,) -> Self {
        self.string = self.string
            .replace("#red", "")
            .replace("#green", "")
            .replace("#yellow", "")
            .replace("#blue", "")
            .replace("#magenta", "")
            .replace("#cyan", "")
            .replace("#white", "")
            .replace("#reset", "")
            .replace("#bold", "")
            .replace("#underline", "");

        self
    }

    #[allow(clippy::inherent_to_string)]
    pub fn to_string(&self) -> String {
        self.string.clone()
    }
}