from .. import register_command, PermissionLevel

import socket

from src.colors import *
from src.db import Database
from src.vars import server_settings_help
from src.functions import hash_password, verify_password, escape_ansi

from init import server_dir, ipaddr, port, \
                 enable_messages, enable_queue, \
                 max_message_length, max_users, \
                 debug_mode, online_mode, update_channel, \
                 afks, queue, users, addresses, user_logged_in, blacklist, \
                 admins_wait_queue, bots_wait_queue, max_registered_users, \
                 special_messages, DatabaseConfig


@register_command("serversettings", arg_count=1, required_permissions=PermissionLevel.ADMIN)
def user_settings_command(socket: socket.socket, username: str, args: list, send):
    cmd_db = Database(server_dir + "/users.db", check_same_thread=False)
    try:
        match args[0]:
            case "help":
                send(f"{server_settings_help}{RESET}")
            
            case "show":
                _base_data = f"""
        {CYAN}IP-Address:{RESET} {ipaddr}
        {CYAN}Port:{RESET} {port}
        {CYAN}Enable Logging Messages:{RESET}{ enable_messages}
        {CYAN}Enable Queue:{RESET} {enable_queue}
        {CYAN}Max Message Length:{RESET} {max_message_length}
        {CYAN}Max Users:{RESET} {max_users}
        {CYAN}Max Registered Users:{RESET} {max_registered_users}
        {CYAN}Debug Mode:{RESET} {debug_mode}
        {CYAN}Online Mode:{RESET} {online_mode}
        {CYAN}Update Channel:{RESET} {update_channel}
        {CYAN}Admins wait Queue:{RESET} {admins_wait_queue}
        {CYAN}Bots wait Queue:{RESET} {bots_wait_queue}
        {CYAN}Special Messages:{RESET} {special_messages}
        {CYAN}Database Driver:{RESET} {DatabaseConfig.driver}
        """
        
        
                message = f"""{GREEN +  Colors.UNDERLINE + Colors.BOLD}Your Server Settings{RESET + Colors.RESET}
        {YELLOW}WARNING:{RESET} This could contain sensible information!
        
        {_base_data}"""
        
                try:
                    if args[1] == "debug":
                        message = f"""{GREEN +  Colors.UNDERLINE + Colors.BOLD}Your Server Settings (Debug){RESET + Colors.RESET}
        {YELLOW}WARNING:{RESET} This could contain sensible information!
        
        {_base_data}
        
        {YELLOW}Afks:{RESET} {afks}
        {YELLOW}Queue:{RESET} {queue.queue}
        {YELLOW}Users:{RESET} {users}
        {YELLOW}Addresses:{RESET} {addresses}
        {YELLOW}Logged in:{RESET} {user_logged_in}
        
        {YELLOW}MySQL Host:{RESET} {DatabaseConfig.host}
        {YELLOW}MySQL Port:{RESET} {DatabaseConfig.port}
        {YELLOW}MySQL ChckThread:{RESET} {DatabaseConfig.chck_thread}
        {YELLOW}MySQL Username:{RESET} {DatabaseConfig.user}
        {YELLOW}MySQL Password:{RESET} {DatabaseConfig.password}
        {YELLOW}MySQL Database:{RESET} {DatabaseConfig.db_name}
            """
                        
                except: pass
                
                send(message)
            
            case _:
                send(f"{Colors.RESET + RED}Invalid subcommand!{RESET + Colors.RESET}")
                    
    except Exception as e: 
        send(f"{RED}Not enough arguments!{RESET}")
        print(e)