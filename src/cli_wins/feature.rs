use libstrawberry::colors::{BOLD, C_RESET, CYAN, RESET, WHITE, YELLOW};

use crate::global::CONFIG;
use crate::utilities::{get_ratelimit_timeout, is_feature_enabled};

pub fn display() {
    println!("\n{BOLD}  {CYAN}* -------------- FEATURES -------------- *{RESET}{C_RESET}");
    println!("{BOLD}  {CYAN}|{WHITE} *{YELLOW} Console Message Logging is {}{CYAN}  |{RESET}{C_RESET}",
             is_feature_enabled(CONFIG.flags.enable_messages)
    );
    println!("{BOLD}  {CYAN}|{WHITE} *{YELLOW} Debug Mode is {}             {CYAN}  |{RESET}{C_RESET}",
             is_feature_enabled(CONFIG.flags.debug_mode)
    );
    println!("{BOLD}  {CYAN}|{WHITE} *{YELLOW} Ratelimit is {}{}        {CYAN}|{RESET}{C_RESET}",
             is_feature_enabled(CONFIG.networking.ratelimit), get_ratelimit_timeout(CONFIG.networking.ratelimit)
    );
    println!("{BOLD}  {CYAN}|{WHITE} *{YELLOW} Online Mode is {}           {CYAN}  |{RESET}{C_RESET}",
             is_feature_enabled(CONFIG.flags.online_mode)
    );
    
    println!("{BOLD}  {CYAN}* -------------------------------------- *{RESET}{C_RESET}\n");
}
