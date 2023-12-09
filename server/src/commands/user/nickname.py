from .. import register_command

import socket

from src.colors import *
from src.db import Database

from init import stbexceptions, User, ClientSender, server_dir, log, debug_logger
from src.functions import userRoleColor

@register_command("nick", arg_count=1)
@register_command("nickname", arg_count=1)
def nickname_command(socket: socket.socket, user: User, args: list, sender: ClientSender):
    cmd_db = Database(server_dir + "/users.db", check_same_thread=False)
    
    cmd = args[0]
    
    # /nick set                        
    try: 
        cmd_db.execute('SELECT role FROM users WHERE username = ?', (user.username,))
        
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
                    sender.send(f"{RED + Colors.BOLD}Please pass a valid argument!{RESET + Colors.RESET}")
                    return

                cmd_db.execute("UPDATE users SET nickname = ? WHERE username = ?", (nick, uname))
                cmd_db.commit()
                
                if nick.lower() == "remove":
                    cmd_db.execute("UPDATE users SET nickname = NULL WHERE username = ?", (uname,))
                    cmd_db.commit()
                    
                    sender.send(f"{GREEN + Colors.BOLD}The nickname of {uname} has been removed{RESET + Colors.RESET}")
                    return 
                
                sender.send(f"{GREEN + Colors.BOLD}The nickname of {uname} has been updated to '{nick}'{RESET + Colors.RESET}")
                return
            
            else:
                sender.send(f"{RED}Sorry, you do not have permissons for that.{RESET}")
                return
        else: 
            sender.send(f"{RED + Colors.BOLD}Please pass a valid argument!{RESET + Colors.RESET}")
        
    else: 
        _cmd = args[0]
                
        if _cmd.lower() == "remove" or _cmd.lower() == "reset":
            cmd_db.execute("UPDATE users SET nickname = NULL WHERE username = ?", (user.username,))
            cmd_db.commit()
            
            sender.send(f"{LIGHTGREEN_EX + Colors.BOLD}Removed nickname{RESET + Colors.RESET}")
            return 
        
        nick = ' '.join(args[0:])
        
        cmd_db.execute("UPDATE users SET nickname = ? WHERE username = ?", (nick, user.username))
        cmd_db.commit()
        
        sender.send(f"{LIGHTGREEN_EX + Colors.BOLD}Changed nickname to {RESET + userRoleColor(user.username)}{nick}{RESET + Colors.RESET}")