import datetime

RED = "\033[1;31m"
YELLOW = "\033[1;33m"
PURPLE = "\033[1;35m"
LIGHT_BLUE = "\033[1;36m"
RESET = "\033[0;0m"

get_time = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")

def strawlog(msg, lvl):
    if lvl == "ERROR":
        print(f"[{get_time}] {RED}[ERROR] {msg}{RESET}")
    elif lvl == "WARN":
        print(f"[{get_time}] {YELLOW}[WARNING] {msg}{RESET}")
    elif lvl == "DEBUG":
        print(f"[{get_time}] {PURPLE}[DEBUG] {msg}{RESET}")
    elif lvl == "INFO":
        print(f"[{get_time}] {LIGHT_BLUE}[INFO] {msg}{RESET}")
    else:
        print(f"[{get_time}] [{lvl}] {msg}")
        
        
    