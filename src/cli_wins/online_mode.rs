use stblib::colors::{BOLD, C_RESET, RESET, YELLOW};

pub fn display() {
    println!("\n{BOLD}  {YELLOW}* --------------- WARNING -------------- *{RESET}{C_RESET}");
    println!("{BOLD}  {YELLOW}|    Online mode is disabled and your    {YELLOW}|{RESET}{C_RESET}");
    println!("{BOLD}  {YELLOW}|       server might be in danger!       {YELLOW}|{RESET}{C_RESET}");
    println!("{BOLD}  {YELLOW}|     Consider using the online mode!    {YELLOW}|{RESET}{C_RESET}");
    println!("{BOLD}  {YELLOW}* -------------------------------------- *{RESET}{C_RESET}\n");
}