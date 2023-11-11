from .. import register_command

import socket

from src.colors import *
from src.db import Database

from init import server_dir, log, debug_logger, stbexceptions
from src.functions import userRoleColor

@register_command("nick", arg_count=1)
@register_command("nickname", arg_count=1)
def nickname_command(socket: socket.socket, username: str, args: list, send):
    cmd_db = Database(server_dir + "/users.db", check_same_thread=False)
    
    cmd = args[0]
    
    # /nick set                        
    try: 
        cmd_db.execute('SELECT role FROM users WHERE username = ?', (username,))
        
    except Exception as e:
        log.error("An SQL error occured!")
        debug_logger(e, stbexceptions.sql_error)
        
    user_role = cmd_db.fetchone()
    
    if cmd == "set":
        if len(args) == 3:
            if user_role[0] == "admin":
                try:
                    uname = args[1]
                    nick = args[2]
                    
                except:
                    send(f"{RED + Colors.BOLD}Please pass a valid argument!{RESET + Colors.RESET}")
                    return

                cmd_db.execute("UPDATE users SET nickname = ? WHERE username = ?", (nick, uname))
                cmd_db.commit()
                
                if nick.lower() == "remove":
                    cmd_db.execute("UPDATE users SET nickname = NULL WHERE username = ?", (uname,))
                    cmd_db.commit()
                    
                    send(f"{GREEN + Colors.BOLD}The nickname of {uname} has been removed{RESET + Colors.RESET}")
                    return 
                
                send(f"{GREEN + Colors.BOLD}The nickname of {uname} has been updated to '{nick}'{RESET + Colors.RESET}")
                return
            
            else:
                send(f"{RED}Sorry, you do not have permissons for that.{RESET}")
                return
        else: 
            send(f"{RED + Colors.BOLD}Please pass a valid argument!{RESET + Colors.RESET}")
        
    else: 
        nick = cmd
                
        if nick.lower() == "remove":
            cmd_db.execute("UPDATE users SET nickname = NULL WHERE username = ?", (username,))
            cmd_db.commit()
            
            send(f"{LIGHTGREEN_EX + Colors.BOLD}Removed nickname{RESET + Colors.RESET}")
            return 
        
        cmd_db.execute("UPDATE users SET nickname = ? WHERE username = ?", (nick, username))
        cmd_db.commit()
        
        send(f"{LIGHTGREEN_EX + Colors.BOLD}Changed nickname to {RESET + userRoleColor(username)}{nick}{RESET + Colors.RESET}")