import datetime

RED = "\033[1;31m"
YELLOW = "\033[1;33m"
PURPLE = "\033[1;35m"
RESET = "\033[0;0m"

get_time = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")

def strawlog(msg, lvl):
    if lvl == "error":
        print(f"[{get_time}] {RED}[ERROR] {msg}{RESET}")
    elif lvl == "warning":
        print(f"[{get_time}] {YELLOW}[WARNING] {msg}{RESET}")
    elif lvl == "debug":
        print(f"[{get_time}] {PURPLE}[DEBUG] {msg}{RESET}")
    else:
        print(f"[{get_time}] [INFO] {msg}")
        
        
    