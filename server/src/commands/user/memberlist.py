from .. import register_command

import socket
import requests

from src.colors import *
from src.db import Database

from init import server_dir, afks, users, config, online_mode, global_ip
from src.vars import api
from src.functions import hasNickname, memberListNickname, isOnline

import yaml
from yaml import SafeLoader


@register_command("memberlist")
@register_command("userlist")
def memberlist_command(socket: socket.socket, username: str, args: list):
    cmd_db = Database(server_dir + "/users.db", check_same_thread=False)
                
    cmd_db.execute("SELECT username FROM users")
    raw_members = cmd_db.fetchall()
    membersLen  = len([raw_members for raw_members in sorted(raw_members)])
    
    cmd_db.execute("SELECT username, badge FROM users WHERE role = 'admin'")
    raw_admins  = cmd_db.fetchall()
    admins_len  = len([raw_admins for raw_admins in sorted(raw_admins)])
    admins      = "\n           ".join([f"{isOnline(result[0])}{LIGHTRED_EX} {memberListNickname(result[0])} [{result[1]}]" for result in raw_admins])
    
    cmd_db.execute("SELECT username, badge FROM users WHERE role = 'bot'")
    raw_bots    = cmd_db.fetchall()
    bots_len    = len([raw_bots for raw_bots in sorted(raw_bots)])
    bots      = "\n           ".join([f"{isOnline(result[0])}{LIGHTMAGENTA_EX} {memberListNickname(result[0])} [{result[1]}]" for result in raw_bots])
    
    
    cmd_db.execute("SELECT username, badge FROM users WHERE role = 'member'")
    raw_members = cmd_db.fetchall()
    members_len = len([raw_members for raw_members in sorted(raw_members)])
    members      = "\n           ".join([f"{isOnline(result[0])}{LIGHTYELLOW_EX} {memberListNickname(result[0])} [{result[1]}]" for result in raw_members])
    
    try:
        if online_mode == True:
            verified = requests.get(api + "server/verified?addr=" + global_ip)
        
            if verified.text == "True":
                verified_txt = f"{GREEN}[VERIFIED]{CYAN} "
            else:
                verified_txt = ""
            
        else:
            verified_txt = ""
        
    except Exception as e: 
        print(e)
    
    onlineUsersLen2 = len([user for user in sorted(users.values())])
                
    socket.send(f"""{CYAN +  Colors.UNDERLINE + Colors.BOLD}{verified_txt}{config['server']['name'].upper()} ({membersLen} Members, {onlineUsersLen2} Online){RESET + Colors.RESET}
        {Colors.BOLD}->{Colors.RESET} {RED}Administrators ({admins_len}){RESET}
           {LIGHTRED_EX}{admins}{RESET}
        
        {Colors.BOLD}->{Colors.RESET} {MAGENTA}Bots ({bots_len}){RESET}
           {LIGHTMAGENTA_EX}{bots}{RESET}
    
        {Colors.BOLD}->{Colors.RESET} {YELLOW}Members ({members_len}){RESET}
           {LIGHTYELLOW_EX}{members}{RESET}
    """
    
    .encode("utf8"))