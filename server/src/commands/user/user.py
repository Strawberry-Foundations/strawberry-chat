from .. import register_command

import socket
import sqlite3 as sql
import datetime

from src.colors import *
from src.db import Database
from src.functions import doesUserExist, userRoleColor, isOnline

from init import server_dir

@register_command("user")
@register_command("member")
def members_command(socket: socket.socket, username: str, args: list, send):
    cmd_db = sql.connect(server_dir + "/users.db", check_same_thread=False)
    cmd_c  = cmd_db.cursor()
    
    try:
        uname = args[0]
        
    except: 
        uname = "me"
    
    if uname.startswith("me"):
        uname = username
    
    if uname == "":
        uname = username
        
    if not doesUserExist(uname):
        send(f"{RED + Colors.BOLD}Sorry, this user does not exist!{RESET + Colors.RESET}")
        return
    
    try:
        cmd_c.execute("SELECT username, nickname, badge, role, role_color, description, badges, discord_name, user_id, strawberry_id, creation_date FROM users WHERE LOWER(username) = ?", (uname.lower(),))
        
    except:
        send(f"{RED + Colors.BOLD}Sorry, this user does not exist!{RESET + Colors.RESET}")
        return
    
    for row in cmd_c:
        role = row[3]
        role_color = row[4]
        
        # Nickname
        if row[1] is not None:
            nickname = row[1]
        else:
            nickname = "Not set"
            
        # Badge
        if row[2] is not None:
            badge = row[2]
        else:
            badge = "Not set"
        
        # Description
        if row[5] is not None:
            description = row[5]
        else:
            description = "Not set"
        
        # Discord Username
        if row[7] is not None:
            discord = MAGENTA + "@" + row[7]
        else:
            discord = "Not set"
            
        # Strawberry ID/Network
        if row[9] is not None:
            strawberry_id_name = MAGENTA + "@" + row[9]
        else:
            strawberry_id_name = "Not set"
            
        role = role.capitalize()
        role_color = role_color.capitalize()
            
        crown_badge         = "- 👑 The legendary founder and owner!"
        cool_badge          = "- 😎 One of the coolest here!"
        flame_badge         = "- 🔥 The hottest user!"
        berryjuice_badge    = "- 🫐 Founder and owner of the Berryjuice Client!"
        bot_badge           = "- 🤖 Just some bot"
        macher_badge        = "- 💪 In germany we say: \"Macher\""
        kindness_badge      = "- 👍 The badge of kindness!"
        troll_badge         = "- 🤡 Someone wo trolls.. watch out"
        evil_badge          = "- 😈 The opposite of the kindness's badge - The evil badge"
        supporter_badge     = "- 🤝 Active supporter and helper"
        newbie_badge        = "- 👋 Say hi! I'm new!"
        og_badge            = "- 😌 A real OG, who is one of the first members!"
        strawberry_badge    = "- 🍓 Strawberry ID & Network user!"
        stbchat_plus_user   = "- 💫 Strawberry Chat+ user"
        all_badges          = ""

        badges = row[6]
        
        if row[6] is None:
            badges = ""
            all_badges = "This user doesn't have any badges yet"
            
        else:
            if "👑" in row[6]:
                all_badges = all_badges + "\n        " + crown_badge  
            if "😎" in row[6]:
                all_badges = all_badges + "\n        " + cool_badge
            if "🔥" in row[6]:
                all_badges = all_badges + "\n        " + flame_badge
            if "🫐" in row[6]:
                all_badges = all_badges + "\n        " + berryjuice_badge
            if "🤖" in row[6]:
                all_badges = all_badges + "\n        " + bot_badge
            if "💪" in row[6]:
                all_badges = all_badges + "\n        " + macher_badge
            if "👍" in row[6]:
                all_badges = all_badges + "\n        " + kindness_badge
            if "🤡" in row[6]:
                all_badges = all_badges + "\n        " + troll_badge
            if "😈" in row[6]:
                all_badges = all_badges + "\n        " + evil_badge
            if "🤝" in row[6]:
                all_badges = all_badges + "\n        " + supporter_badge
            if "👋" in row[6]:
                all_badges = all_badges + "\n        " + newbie_badge
            if "😌" in row[6]:
                all_badges = all_badges + "\n        " + og_badge
            if "🍓" in row[6] or row[9] is not None:
                all_badges = all_badges + "\n        " + strawberry_badge
            if "💫" in row[6]:
                all_badges = all_badges + "\n        " + stbchat_plus_user
            
            
        send(
            f"""{CYAN + Colors.BOLD + Colors.UNDERLINE}User profile of {row[0]}{RESET + Colors.RESET} {isOnline(row[0])}
        {GREEN + Colors.BOLD}Username:{RESET + userRoleColor(row[0])} @{row[0].lower()}{RESET + Colors.RESET}
        {GREEN + Colors.BOLD}User-ID:{RESET + LIGHTBLUE_EX} {row[8]}{RESET + Colors.RESET}
        {GREEN + Colors.BOLD}Nickname:{RESET + Colors.BOLD} {nickname}{RESET + Colors.RESET}
        {GREEN + Colors.BOLD}Description:{RESET + Colors.BOLD} {description}{RESET + Colors.RESET}
        {GREEN + Colors.BOLD}Member since:{RESET + Colors.BOLD} {datetime.datetime.fromtimestamp(row[10]).strftime("%a, %d. %h %Y")}{RESET + Colors.RESET}
        {GREEN + Colors.BOLD}Main Badge:{RESET + Colors.BOLD} {badge}{RESET + Colors.RESET}
        {GREEN + Colors.BOLD}Badges: {badges}{RESET + Colors.BOLD}{RESET + Colors.RESET}{Colors.BOLD}{all_badges}{Colors.RESET}
        {GREEN + Colors.BOLD}Role:{RESET + Colors.BOLD} {role}{RESET + Colors.RESET}
        {GREEN + Colors.BOLD}Role Color:{RESET + Colors.BOLD} {userRoleColor(row[0])}{role_color}{RESET + Colors.RESET}
        {GREEN + Colors.BOLD}Strawberry Network:{RESET + Colors.BOLD} {strawberry_id_name}{RESET + Colors.RESET}
        {GREEN + Colors.BOLD}Discord:{RESET + Colors.BOLD} {discord}{RESET + Colors.RESET}\n"""
            )