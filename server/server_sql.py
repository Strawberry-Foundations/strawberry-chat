#!/usr/bin/env python3

import logging
import atexit
from colorama import Fore, Style
import socket
import threading
import json
import os
from os.path import exists
import sys
import datetime
import sqlite3 as sql
import time
import errno
import random

# Alias for colorama colors
BLACK           = Fore.BLACK
RED             = Fore.RED
GREEN           = Fore.GREEN
YELLOW          = Fore.YELLOW
BLUE            = Fore.BLUE
MAGENTA         = Fore.MAGENTA
CYAN            = Fore.CYAN
WHITE           = Fore.WHITE
RESET           = Fore.RESET

LIGHTBLACK_EX   = Fore.LIGHTBLACK_EX
LIGHTRED_EX     = Fore.LIGHTRED_EX
LIGHTGREEN_EX   = Fore.LIGHTGREEN_EX
LIGHTYELLOW_EX  = Fore.LIGHTYELLOW_EX
LIGHTBLUE_EX    = Fore.LIGHTBLUE_EX
LIGHTMAGENTA_EX = Fore.LIGHTMAGENTA_EX
LIGHTCYAN_EX    = Fore.LIGHTCYAN_EX
LIGHTWHITE_EX   = Fore.LIGHTWHITE_EX

# Init logger
class LogFormatter(logging.Formatter):
    format = "[%(asctime)s] [%(levelname)s] %(message)s"

    FORMATS = {
        logging.DEBUG:    WHITE  + Style.DIM    + format,
        logging.INFO:     BLUE   + format,
        logging.WARNING:  YELLOW + format,
        logging.ERROR:    RED    + Style.BRIGHT + format,
        logging.CRITICAL: RED    + format
    }

    def format(self, record):
        log_fmt = Style.RESET_ALL + self.FORMATS.get(record.levelno) + Style.RESET_ALL
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


log = logging.getLogger("LOG")

if os.environ.get("LOG_LEVEL") is not None:
    log.setLevel(os.environ.get("LOG_LEVEL").upper())
else:
    log.setLevel("INFO")
    
log_fh = logging.FileHandler('log.txt')
log_fmt = logging.Formatter("%(asctime)s [%(levelname)s]  %(message)s")
log_fh.setFormatter(log_fmt)
log_ch = logging.StreamHandler()
log_ch.setFormatter(LogFormatter())
log.addHandler(log_ch)
log.addHandler(log_fh)

#log.debug("DEBUG MESSAGE")
#log.info("INFO MESSAGE")
#log.warning("WARNING MESSAGE")
#log.error("ERROR MESSAGE")
#log.critical("CRITICAL MEESAGE")

# Path of server.py
server_dir = os.path.dirname(os.path.realpath(__file__))

# Connect to the database
db = sql.connect(server_dir + "/users.db", check_same_thread=False)
c = db.cursor()

with open(server_dir + "/config.json", "r") as f:
    config = json.load(f)

# Configuration
ipaddr = config["address"]
port = config["port"]
enable_messages = config["enable_messages"]
max_message_length = config["max_message_length"]
debug_mode = config["debug_mode"]

# Version-specified Variables 
short_ver = "1.7.0_b5"
ver = short_ver + "-vc_sql"
chat_name = "Strawberry Chat"
codename = "Vanilla Cake"
server_edition = "SQL Server"

# Afk list
afks = list([])
blacklist = set()

# Blacklisted word functions
def open_blacklist():
    with open(server_dir + "/blacklist.txt", "r") as f:
        for word in f:
            word = word.strip().lower()
            blacklist.add(word)    

def create_empty_file(filename):
    with open(server_dir + "/" + filename, "w") as ef:
        pass

# Blacklisted words set
if exists(server_dir + "/blacklist.txt"):
    open_blacklist()
    
else:
    create_empty_file("blacklist.txt")
    open_blacklist()


class Time:
    def currentTime():
        time = datetime.datetime.now()
        formattedTime = time.strftime("%H:%M:%S")
        return formattedTime

    def currentDate():
        date = datetime.date.today()
        formattedDate = date.strftime("%Y-%m-%d")
        return formattedDate

class Colors:
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    RESET = '\033[0m'
    GRAY = "\033[90m"
    
if "--enable-messages" in sys.argv:
    enable_messages = True

# General Functions
def userNickname(uname):
    c = db.cursor()
    c.execute('SELECT nickname FROM users WHERE username = ?', (uname,))
    unick = c.fetchone()
    
    if unick[0] is not None: 
        unick = unick[0]
        return unick

def hasNickname(uname):
    c = db.cursor()
    c.execute('SELECT nickname FROM users WHERE username = ?', (uname,))
    unick = c.fetchone()
    
    if unick[0] is not None: 
        return True
    
    else: 
        return False

def userRoleColor(uname):
    c = db.cursor()
    c.execute('SELECT role_color FROM users WHERE username = ?', (uname,))
    color = c.fetchone()
    
    if color[0] is not None: 
        match color[0]:
            case "red": 
                return RED + Colors.BOLD
            
            case "green": 
                return GREEN + Colors.BOLD
                
            case "cyan": 
                return CYAN + Colors.BOLD
            
            case "blue": 
                return BLUE

            case "yellow": 
                return YELLOW
                
            case "magenta": 
                return MAGENTA
            
            case "lightred":
                return LIGHTRED_EX
            
            case "lightgreen":
                return LIGHTGREEN_EX
            
            case "lightcyan":
                return LIGHTCYAN_EX
            
            case "lightblue":
                return LIGHTBLUE_EX

            case "lightyellow":
                return LIGHTYELLOW_EX

            case "lightmagenta":
                return LIGHTMAGENTA_EX
            
            case "boldred":
                return Colors.BOLD + RED

            case "boldgreen":
                return Colors.BOLD + GREEN
            
            case "boldcyan":
                return Colors.BOLD + CYAN
            
            case "boldblue":
                return Colors.BOLD + BLUE
            
            case "boldyellow":
                return Colors.BOLD + YELLOW
            
            case "boldmagenta":
                return Colors.BOLD + MAGENTA
            
            case _:
                return RESET
    else: 
        return RESET

def isMuted(uname):
    c = db.cursor()
    c.execute('SELECT muted FROM users WHERE username = ?', (uname,))
    mutedStatus = c.fetchone()
    
    if mutedStatus[0] == "true":
        return True
    else: 
        return False

def isAccountEnabled(uname):
    c = db.cursor()
    c.execute('SELECT accountEnabled FROM users WHERE username = ?', (uname,))
    accountEnabledStatus = c.fetchone()
    
    if accountEnabledStatus[0] == "true":
        return True
    else: 
        return False
    
def debugLogger(errorMessage, errorCode):
    if debug_mode:
        log.error(f"ErrCode {errorCode}: {errorMessage}")
    else:
        None
        
def sqlError(errorMessage):
    log.error(f"e096: An SQL Error occured: {errorMessage}")


def doesUserExist(uname):
    uname = uname.lower()

    c = db.cursor()
    c.execute('SELECT username FROM users WHERE LOWER(username) = ?', (uname,))
    
    try:
        userExists = c.fetchone()[0]
        
    except:
        return False
    
    if userExists.lower() == uname:
        return True
    
    
    
# News
news = f"""{GREEN +  Colors.UNDERLINE + Colors.BOLD}{chat_name} News - v1.7.0 Beta{RESET + Colors.RESET}{CYAN + Colors.BOLD}
        - COMMUNITY: New custom client by matteodev8: superchrgd ⚡ (Currently in development)
        - NEW: Bots are here!
               You can now create and program your own bots - so
               you can create your own commands, independent of the server! 
        - NEW: User Profiles are here! You can now link your discord, write something 
               about yourself in your description or take a look at your fantastic badges!
        - NEW: You can now create an account from the login page!
        - NEW: Fancy User Chat Badges and exclusive badges for your user profile!
        - NEW: Blacklisted Words
        - NEW: Character Limit with some special easter eggs :)
        - NEW: User Nicknames and command to change nickname
        - NEW: Member Command
        - NEW: User info command
        - NEW: New welcome message with chat color support
        - ADMIN: Broadcast Command, Mute Command, Role set/get/color Command, Bwords set/get/add/reload Command and Ban Command
        - FIX: Fixed many many bugs{RESET + Colors.RESET}"""



def connectionThread(sock):
    while True:
        try:
            client, address = sock.accept()

        except Exception as e:
            log.error("A connection error occured!")
            debugLogger(e, "001")
            
            break
        
        log.info(f"{address[0]} has connected")
        
        addresses[client] = address
        threading.Thread(target=clientThread, args=(client,)).start()


def clientThread(client):
    address = addresses[client][0]
    
    try:
        user = clientLogin(client)
            
    except Exception as e:
        log.error(f"A login error with {address} occured!")
        debugLogger(e, "002")
        
        del addresses[client]
        return
    
    log.info(f"{user} ({address}) logged in")

    users[client] = user

    try:
        client.send(f"{CYAN + Colors.BOLD}Welcome back {user}! Nice to see you!{RESET + Colors.RESET}".encode("utf8"))
        onlineUsersLen = len([user for user in sorted(users.values())])
        
        if onlineUsersLen == 1:
            onlineUsersStr = f"is {onlineUsersLen} user"
        else:
            onlineUsersStr = f"are {onlineUsersLen} users"
            
        time.sleep(0.05)
        client.send(f"""{CYAN + Colors.BOLD}Currently there {onlineUsersStr} online. For help use /help{RESET + Colors.RESET}\n{news}""".encode("utf8"))
        

    except Exception as e:
        log.error(f"A Communication error with {address} ({user}) occurred.")
        debugLogger(e, "003")
        
        del addresses[client]
        del users[client]
        client.close()
        return
    
    time.sleep(0.1)
    broadcast(f"{Colors.GRAY + Colors.BOLD}-->{Colors.RESET} {userRoleColor(user)}{user}{GREEN + Colors.BOLD} has joined the chat room!{RESET + Colors.RESET}")

    while True:
        try:
            message = client.recv(2048).decode("utf8")
            message_length = len(message)
        
            # Message length control system
            rnd = random.randint(0, 3)    
            if message_length > max_message_length:
                if rnd == 0:
                    client.send(f"{YELLOW + Colors.BOLD}Your message is too long.{RESET + Colors.RESET}".encode("utf8"))
                    
                elif rnd == 1:
                    client.send(f"{YELLOW + Colors.BOLD}boah digga halbe bibel wer liest sich das durch{RESET + Colors.RESET}".encode("utf8"))
                    
                elif rnd == 2:
                    client.send(f"{YELLOW + Colors.BOLD}junge niemand will sich hier die herr der ringe trilogie durchlesen{RESET + Colors.RESET}".encode("utf8"))
                    
                elif rnd == 3:
                    client.send(f"{YELLOW + Colors.BOLD}ne digga das liest sich doch keiner durch grundgesetz einfach. mach dich ab{RESET + Colors.RESET}".encode("utf8"))
                    client.close()
                continue

            # Blacklisted Word System
            c.execute('SELECT role FROM users WHERE username = ?', (user,))    
            res = c.fetchone()
            
            c.execute('SELECT enableBlacklistedWords FROM users WHERE username = ?', (user,))
            res2 = c.fetchone()
            
            if res[0] == "admin" or res2[0] == "false":
                pass
            
            else:
                for word in message.split():
                    word = word.lower()
                    
                    if word in blacklist:
                        client.send(f"{YELLOW + Colors.BOLD}Please be friendlier in the chat. Rejoin when you feel ready!{RESET + Colors.RESET}".encode("utf8"))
                        client.close()
                        
                    else:
                        pass
            
            # Define db variable global
            global db
                    
            # /broadcast Command            
            if message.startswith("/broadcast ") or message.startswith("/rawsay "):
                try: 
                    c.execute('SELECT role FROM users WHERE username = ?', (user,))
                    
                except Exception as e:
                    sqlError(e)
                    
                res = c.fetchone()
                
                if res[0] == "admin":
                    text = message.replace("/broadcast ", "")
                    
                    if message.startswith("/broadcast "):
                        text = message.replace("/broadcast ", "")
                        
                    elif message.startswith("/rawsay "):
                        text = message.replace("/rawsay ", "")
                    
                    if message == "/broadcast " or message == "/rawsay ":
                        client.send(f"{RED + Colors.BOLD}Wrong usage{RESET + Colors.RESET}".encode("utf8"))
                        continue
                    
                    broadcast(f"{text}")
                    continue
                    
                else:
                    client.send(f"{RED}Sorry, you do not have permissons for that.{RESET}".encode("utf8"))
                    continue
            
    
            # /nick Command
            elif message.startswith("/nick ") or message.startswith("/nickname "):  
                if message.startswith("/nick "):
                    nick = message.replace("/nick ", "")
                    
                elif message.startswith("/nickname ") :
                    nick = message.replace("/nickname ", "")
                    
                if nick.lower() == "remove":
                    c.execute("UPDATE users SET nickname = NULL WHERE username = ?", (user,))
                    db.commit()
                    
                    client.send(f"{LIGHTGREEN_EX + Colors.BOLD}Removed nickname{RESET + Colors.RESET}".encode("utf8"))
                    continue
                    
                c.execute("UPDATE users SET nickname = ? WHERE username = ?", (nick, user))
                db.commit()
                
                client.send(f"{LIGHTGREEN_EX + Colors.BOLD}Changed nickname to {RESET + userRoleColor(user)}{nick}{RESET + Colors.RESET}".encode("utf8"))
                continue
            
            
            # /member Command
            elif message.startswith("/member ") or message.startswith("/user ") or message.startswith("/userinfo "):  
                if message.startswith("/member "):
                    uname = message.replace("/member ", "")
                    
                elif message.startswith("/user "):
                    uname = message.replace("/user ", "")
                    
                elif message.startswith("/userinfo "):
                    uname = message.replace("/userinfo ", "")
                    
                if uname.startswith("me"):
                    uname = user
                
                if uname == "":
                    uname = user
                
                try:
                    c.execute("SELECT username, nickname, badge, role, role_color, description, badges, discord_name FROM users WHERE username = ?", (uname,))
                    
                except:
                    client.send(f"{RED + Colors.BOLD}User not found.{RESET + Colors.RESET}".encode("utf8"))
                    continue
                
                for row in c:
                    
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
                        
                    role = role.capitalize()
                    role_color = role_color.capitalize()
                        
                    crown_badge = "- 👑 The legendary founder and owner!"
                    cool_badge = "- 😎 One of the coolest here!"
                    flame_badge = "- 🔥 The hottest user!"
                    lightning_badge = "- ⚡ Founder and owner of the Superchrgd Client!"
                    bot_badge = "- 🤖 Just some bot"
                    macher_badge = "- 💪 In germany we say: \"Macher\""
                    kindness_badge = "- 👍 The badge of kindness!"
                    troll_badge = "- 🤡 Someone wo trolls.. watch out"
                    evil_badge = "- 😈 The opposite of the kindness's badge - The evil badge"
                    supporter_badge = "- 🤝 Active supporter and helper"
                    newbie_badge = "- 👋 Say hi! I'm new!"
                    og_badge = "- 😌 A real OG, who is one of the first members!"
                    all_badges = ""

                    if row[6] is None:
                        all_badges = " Hmm... This user doesn't have any badges yet"
                        
                    else:
                        if "👑" in row[6]:
                            all_badges = all_badges + "\n        " + crown_badge  
                        if "😎" in row[6]:
                            all_badges = all_badges + "\n        " + cool_badge
                        if "🔥" in row[6]:
                            all_badges = all_badges + "\n        " + flame_badge
                        if "⚡" in row[6]:
                            all_badges = all_badges + "\n        " + lightning_badge
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
                        
                        
                    client.send(
                        f"""{CYAN + Colors.BOLD + Colors.UNDERLINE}User information about {row[0]}{RESET + Colors.RESET}
        {GREEN + Colors.BOLD}Username:{RESET + userRoleColor(row[0])} @{row[0].lower()}{RESET + Colors.RESET}
        {GREEN + Colors.BOLD}User-ID:{RESET + LIGHTBLUE_EX} 0{RESET + Colors.RESET}
        {GREEN + Colors.BOLD}Nickname:{RESET + Colors.BOLD} {nickname}{RESET + Colors.RESET}
        {GREEN + Colors.BOLD}Description:{RESET + Colors.BOLD} {description}{RESET + Colors.RESET}
        {GREEN + Colors.BOLD}Main Badge:{RESET + Colors.BOLD} {badge}{RESET + Colors.RESET}
        {GREEN + Colors.BOLD}Badges: {row[6]}{RESET + Colors.BOLD}{RESET + Colors.RESET}{Colors.BOLD}{all_badges}{Colors.RESET}
        {GREEN + Colors.BOLD}Role:{RESET + Colors.BOLD} {role}{RESET + Colors.RESET}
        {GREEN + Colors.BOLD}Role Color:{RESET + Colors.BOLD} {userRoleColor(row[0])}{role_color}{RESET + Colors.RESET}
        {GREEN + Colors.BOLD}Discord:{RESET + Colors.BOLD} {discord}{RESET + Colors.RESET}"""
                        .encode("utf8"))
                continue
                
                
            # /mute Command
            elif message.startswith("/mute "):
                try: 
                    c.execute('SELECT role FROM users WHERE username = ?', (user,))
                    
                except Exception as e:
                    sqlError(e)
                    
                res = c.fetchone()
                
                if res[0] == "admin":
                    uname = message.replace("/mute ", "")
                    
                    c.execute("UPDATE users SET muted = 'true' WHERE username = ?", (uname,))
                    db.commit()
                    
                    client.send(f"{LIGHTGREEN_EX + Colors.BOLD}Muted {uname}{RESET + Colors.RESET}".encode("utf8"))
                    continue
                    
                else:
                    client.send(f"{RED}Sorry, you do not have permissons for that.{RESET}".encode("utf8"))
                    
                    
            # /unmute Command
            elif message.startswith("/unmute "):
                try: 
                    c.execute('SELECT role FROM users WHERE username = ?', (user,))
                    
                except Exception as e:
                    sqlError(e)
                    
                res = c.fetchone()
                
                if res[0] == "admin":
                    uname = message.replace("/unmute ", "")
                    
                    c.execute("UPDATE users SET muted = 'false' WHERE username = ?", (uname,))
                    db.commit()
                    
                    client.send(f"{LIGHTGREEN_EX + Colors.BOLD}Unmuted {uname}{RESET + Colors.RESET}".encode("utf8"))
                    continue
                    
                else:
                    client.send(f"{RED}Sorry, you do not have permissons for that.{RESET}".encode("utf8"))
            
            
            # /discord Command
            elif message.startswith("/discord "):
                discord_name = message.replace("/discord ", "")

                if discord_name.lower() == "remove":
                    c.execute("UPDATE users SET discord_name = NULL WHERE username = ?", (user,))
                    db.commit()
                    
                    client.send(f"{LIGHTGREEN_EX + Colors.BOLD}Removed Discord Link{RESET + Colors.RESET}".encode("utf8"))
                    continue
                
                c.execute("UPDATE users SET discord_name = ? WHERE username = ?", (discord_name, user))
                db.commit()
                
                client.send(f"{LIGHTGREEN_EX + Colors.BOLD}Changed Discord Link to {MAGENTA}{discord_name}{RESET + Colors.RESET}".encode("utf8"))
                continue

            
            # /description Command
            elif message.startswith("/description "):
                desc = message.replace("/description ", "")

                if desc.lower() == "remove" or desc.lower() == "reset":
                    c.execute("UPDATE users SET description = NULL WHERE username = ?", (user,))
                    db.commit()
                    
                    client.send(f"{LIGHTGREEN_EX + Colors.BOLD}Removed Description{RESET + Colors.RESET}".encode("utf8"))
                    continue
                
                elif desc.lower() == "" or desc.lower() == " ":
                    c.execute("SELECT description FROM users WHERE username = ?", (user,))
                    desc = c.fetchone()[0]
                    
                    client.send(f"{LIGHTGREEN_EX + Colors.BOLD}Your current description: {RESET}{desc}{Colors.RESET}".encode("utf8"))
                    continue
                
                c.execute("UPDATE users SET description = ? WHERE username = ?", (desc, user))
                db.commit()
                
                client.send(f"{LIGHTGREEN_EX + Colors.BOLD}Changed Description to {CYAN}{desc}{RESET + Colors.RESET}".encode("utf8"))
                continue

        
            # /ban Command
            elif message.startswith("/ban "):
                try: 
                    c.execute('SELECT role FROM users WHERE username = ?', (user,))
                    
                except Exception as e:
                    sqlError(e)
                    
                res = c.fetchone()
                
                if res[0] == "admin":
                    uname = message.replace("/ban ", "")
                    
                    c.execute("UPDATE users SET accountEnabled = 'false' WHERE username = ?", (uname,))
                    db.commit()
                    
                    client.send(f"{LIGHTGREEN_EX + Colors.BOLD}Banned {uname}{RESET + Colors.RESET}".encode("utf8"))
                    continue
                    
                else:
                    client.send(f"{RED}Sorry, you do not have permissons for that.{RESET}".encode("utf8"))
            
            
            # /unban Command
            elif message.startswith("/unban "):
                try: 
                    c.execute('SELECT role FROM users WHERE username = ?', (user,))
                    
                except Exception as e:
                    sqlError(e)
                    
                res = c.fetchone()
                
                if res[0] == "admin":
                    uname = message.replace("/unban ", "")
                    
                    c.execute("UPDATE users SET accountEnabled = 'true' WHERE username = ?", (uname,))
                    db.commit()
                    
                    client.send(f"{LIGHTGREEN_EX + Colors.BOLD}Unbanned {uname}{RESET + Colors.RESET}".encode("utf8"))
                    continue
                    
                else:
                    client.send(f"{RED}Sorry, you do not have permissons for that.{RESET}".encode("utf8"))
            
            
            # /role Command
            elif message.startswith("/role "):
                try: 
                    c.execute('SELECT role FROM users WHERE username = ?', (user,))
                    
                except Exception as e: 
                    sqlError(e)
                    
                res = c.fetchone()
                
                if res[0] == "admin":
                    arg = message.replace("/role ", "")
                    args = arg.split(" ")

                    cmd = args[0]
                    
                    # /role set Command
                    if cmd == "set":
                        try:
                            uname = args[1]
                            role = args[2]
                        
                            c.execute("UPDATE users SET role = ? WHERE username = ?", (role, uname))
                            db.commit()
                            
                            client.send(f"{LIGHTGREEN_EX + Colors.BOLD}Role of {uname} was set to {role}{RESET + Colors.RESET}".encode("utf8"))
                            continue
                        
                        except:
                            client.send(f"{RED + Colors.BOLD}Invalid username and/or role!{RESET + Colors.RESET}".encode("utf8"))
                            continue
                    
                    # /role get Command
                    elif cmd == "get":
                        try:
                            uname = args[1]
                      
                            c.execute("SELECT role FROM users WHERE username = ?", (uname,))
                            role = c.fetchone()[0]
                            
                            client.send(f"{LIGHTGREEN_EX + Colors.BOLD}Role of {uname}: {MAGENTA}{role}{RESET + Colors.RESET}".encode("utf8"))
                            continue
                        
                        except:
                            client.send(f"{RED + Colors.BOLD}Invalid username!{RESET + Colors.RESET}".encode("utf8"))
                            continue
                    
                    # /role color Command
                    elif cmd == "color":
                        try:
                            uname = args[1]
                            color = args[2]
                        
                            c.execute("UPDATE users SET role_color = ? WHERE username = ?", (color, uname))
                            db.commit()
                            
                            client.send(f"{LIGHTGREEN_EX + Colors.BOLD}Role Color of {uname} was set to {color}{RESET + Colors.RESET}".encode("utf8"))
                            continue
                    
                        except:
                            client.send(f"{RED + Colors.BOLD}Invalid username and/or color!{RESET + Colors.RESET}".encode("utf8"))
                            continue
                        
                    else:
                        client.send(f"{RED + Colors.BOLD}Invalid command usage.{RESET + Colors.RESET}".encode("utf8"))
                        continue
                    
                else:
                    client.send(f"{RED}Sorry, you do not have permissons for that.{RESET}".encode("utf8"))
            
            
            # /bwords Command
            elif message.startswith("/bwords "):
                try: 
                    c.execute('SELECT role FROM users WHERE username = ?', (user,))
                    
                except Exception as e:
                    sqlError(e)
                    
                res = c.fetchone()
                
                if res[0] == "admin":
                    arg = message.replace("/bwords ", "")
                    args = arg.split(" ")

                    cmd = args[0]
                    
                    # /bwords set
                    if cmd == "set":
                        try:
                            uname = args[1]
                            value = args[2]
                         
                            c.execute("UPDATE users SET enableBlacklistedWords = ? WHERE username = ?", (value, uname))
                            db.commit()
                        
                            if value == "true":
                                client.send(f"{LIGHTGREEN_EX + Colors.BOLD}Enabled Blacklisted Words for {uname}{RESET + Colors.RESET}".encode("utf8"))
                                continue
                            
                            elif value == "false":
                                client.send(f"{LIGHTGREEN_EX + Colors.BOLD}Disabled Blacklisted Words for {uname}{RESET + Colors.RESET}".encode("utf8"))
                                continue
                            
                            else:
                                client.send(f"{RED + Colors.BOLD}Invalid value!{RESET + Colors.RESET}".encode("utf8"))
                                continue
                    
                        except:
                            client.send(f"{RED + Colors.BOLD}Invalid username and/or value!{RESET + Colors.RESET}".encode("utf8"))
                            continue
                        
                    # /bwords get
                    elif cmd == "get":
                        try:
                            uname = args[1]
                                
                            c.execute("SELECT enableBlacklistedWords FROM users WHERE username = ?", (uname,))
                            value = c.fetchone()[0]
                            
                            if value == "true":
                                client.send(f"{LIGHTGREEN_EX + Colors.BOLD}Blacklisted Words for {uname} are enabled{RESET + Colors.RESET}".encode("utf8"))
                                continue
                            
                            elif value == "false":
                                client.send(f"{LIGHTGREEN_EX + Colors.BOLD}Blacklisted Words for {uname} are disabled{RESET + Colors.RESET}".encode("utf8"))
                                continue
                            
                            else:
                                client.send(f"{RED + Colors.BOLD}Whoa! This should not happen...{RESET + Colors.RESET}".encode("utf8"))
                                continue
                        except:
                            client.send(f"{RED + Colors.BOLD}Invalid username{RESET + Colors.RESET}".encode("utf8"))
                            continue
                           
                    # /bwords add 
                    elif cmd == "add":
                        try:
                            word = args[1]
                        except:
                            client.send(f"{RED + Colors.BOLD}Cant add an empty word!{RESET + Colors.RESET}".encode("utf8"))
                            continue
                        
                        if word == "":
                            client.send(f"{RED + Colors.BOLD}Cant add an empty word!{RESET + Colors.RESET}".encode("utf8"))
                            continue
                        
                        with open("blacklist.txt", "a") as f:
                            f.write("\n" + word)
                            f.close()
                        
                        client.send(f"{LIGHTGREEN_EX + Colors.BOLD}Added '{word}' to the blacklist{RESET + Colors.RESET}".encode("utf8"))
                        continue
                    
                    # /bwords reload
                    elif cmd == "reload":
                        try: 
                            c.execute('SELECT role FROM users WHERE username = ?', (user,))
                            
                        except Exception as e:
                            sqlError(e)
                            
                        res = c.fetchone()
                        
                        if res[0] == "admin":
                            with open("blacklist.txt", "r") as f:
                                for word in f:
                                    word = word.strip().lower()
                                    blacklist.add(word)
                            
                        else:
                            client.send(f"{RED}Sorry, you do not have permissons for that.{RESET}".encode("utf8"))
                            
                    else:
                        client.send(f"{RED + Colors.BOLD}Invalid command usage.{RESET + Colors.RESET}".encode("utf8"))
                        continue
                    
                else:
                    client.send(f"{RED}Sorry, you do not have permissons for that.{RESET}".encode("utf8"))
            
            
            # /badge Command
            elif message.startswith("/badge "):
                try: 
                    c.execute('SELECT role FROM users WHERE username = ?', (user,))
                    
                except Exception as e:
                    sqlError(e)
                    
                res = c.fetchone()
                
                if res[0] == "admin":
                    arg = message.replace("/badge ", "")
                    args = arg.split(" ")

                    cmd = args[0]
                    
                    # /badge add
                    if cmd == "add":
                        # If no username is provided
                        if len(args) == 2:
                            try:
                                badge_to_add = args[1]
                                
                            except:
                                client.send(f"{RED + Colors.BOLD}Please pass a valid argument!{RESET + Colors.RESET}".encode("utf8"))
                                continue
                                
                            c.execute("SELECT badges FROM users WHERE username = ?", (user,))
                            
                            user_badges = c.fetchone()[0]
                            
                            # Does the user already have this badge?
                            if badge_to_add in user_badges:
                                client.send(f"{RED + Colors.BOLD}This badge is already assigned to your profile!{RESET + Colors.RESET}".encode("utf8"))
                                continue
                            
                            new_user_badges = user_badges + badge_to_add
                            
                            c.execute("UPDATE users SET badges = ? WHERE username = ?", (new_user_badges, user))
                            db.commit()
                            
                            client.send(f"{GREEN + Colors.BOLD}Added badge '{badge_to_add}' to your user profile{RESET + Colors.RESET}".encode("utf8"))
                            continue
                        
                        # If username is provided
                        elif len(args) == 3:
                            try:
                                badge_to_add = args[1]
                                uname = args[2]
                                
                            except:
                                client.send(f"{RED + Colors.BOLD}Please pass a valid argument!{RESET + Colors.RESET}".encode("utf8"))
                                continue
                                
                            if doesUserExist(uname) == False:
                                client.send(f"{RED + Colors.BOLD}Sorry, this user does not exist!{RESET + Colors.RESET}".encode("utf8"))
                                continue
                            
                            else: 
                                c.execute("SELECT badges FROM users WHERE username = ?", (uname,))
                            
                                user_badges = c.fetchone()[0]
                                
                                # Does the user already have this badge?
                                if badge_to_add in user_badges:
                                    client.send(f"{RED + Colors.BOLD}This badge is already assigned to {uname}'s profile!{RESET + Colors.RESET}".encode("utf8"))
                                    continue
                                
                                new_user_badges = user_badges + badge_to_add
                                
                                c.execute("UPDATE users SET badges = ? WHERE username = ?", (new_user_badges, uname))
                                db.commit()
                                
                                client.send(f"{GREEN + Colors.BOLD}Added badge '{badge_to_add}' to {uname}'s profile{RESET + Colors.RESET}".encode("utf8"))
                                continue
                            
                        elif len(args) < 2 or len(args) > 3:
                            client.send(f"{RED + Colors.BOLD}Invalid command usage.{RESET + Colors.RESET}".encode("utf8"))
                            continue
                                            
                else:
                    client.send(f"{RED}Sorry, you do not have permissons for that.{RESET}".encode("utf8"))
                    continue

                # /badge set
                if cmd == "set":
                    # If no username is provided
                    if len(args) == 2:
                        try:
                            badge_to_set = args[1]
                            
                        except:
                            client.send(f"{RED + Colors.BOLD}Please pass a valid argument!{RESET + Colors.RESET}".encode("utf8"))
                            continue
                            
                        c.execute("SELECT badges FROM users WHERE username = ?", (user,))
                        
                        user_badges = c.fetchone()[0]
                        
                        # Does the user have this badge?
                        if badge_to_set in user_badges:
                        
                            c.execute("UPDATE users SET badge = ? WHERE username = ?", (badge_to_set, user))
                            db.commit()
                            
                            client.send(f"{GREEN + Colors.BOLD}The main badge of you has been updated to '{badge_to_set}'{RESET + Colors.RESET}".encode("utf8"))
                            continue
                        
                        else:
                            client.send(f"{RED + Colors.BOLD}You do not own this badge!{RESET + Colors.RESET}".encode("utf8"))
                            continue
                        
                    # If username is provided
                    elif len(args) == 3:
                        if res[0] == "admin":
                            try:
                                badge_to_set = args[1]
                                uname = args[2]
                                
                                if uname == "":
                                    client.send(f"{RED + Colors.BOLD}Please provide a valid username! If you try to change your own main badge, please do not add a space after the badge!{RESET + Colors.RESET}".encode("utf8"))
                                    continue
                                
                            except:
                                client.send(f"{RED + Colors.BOLD}Please pass a valid argument!{RESET + Colors.RESET}".encode("utf8"))
                                continue
                                
                            if doesUserExist(uname) == False:
                                client.send(f"{RED + Colors.BOLD}Sorry, this user does not exist!{RESET + Colors.RESET}".encode("utf8"))
                                continue
                            
                            else: 
                                c.execute("SELECT badges FROM users WHERE username = ?", (uname,))
                            
                                user_badges = c.fetchone()[0]
                                
                                # Does the user have this badge?
                                if badge_to_set in user_badges:
                                        
                                    c.execute("UPDATE users SET badge = ? WHERE username = ?", (badge_to_set, uname))
                                    db.commit()
                                    
                                    client.send(f"{GREEN + Colors.BOLD}The main badge of {uname} has been updated to '{badge_to_set}'{RESET + Colors.RESET}".encode("utf8"))
                                    continue
                                
                                else:
                                    client.send(f"{RED + Colors.BOLD}This user does not own this badge!{RESET + Colors.RESET}".encode("utf8"))
                                    continue
                        else:
                            client.send(f"{RED}Sorry, you do not have permissons for that.{RESET}".encode("utf8"))
                            continue
                        
                    elif len(args) < 2 or len(args) > 3:
                        client.send(f"{RED + Colors.BOLD}Invalid command usage.{RESET + Colors.RESET}".encode("utf8"))
                        continue
                

            # Match-Case-Pattern Commands
            match message:
                # Quit / Exit Command
                case "/quit" | "/exit":
                    client.send(f"{YELLOW + Colors.BOLD}You left the chat!{RESET + Colors.RESET}".encode("utf8"))
                    del addresses[client]
                    del users[client]
                    client.close()
                    
                    log.info(f"[<] {address} ({user}) has left.")
                    broadcast(f"{YELLOW + Colors.BOLD}<- {userRoleColor(user)}{user}{YELLOW + Colors.BOLD} has left the chat.{RESET + Colors.RESET}")
                    break


                # Help Command
                case "/help":
                    broadcast(f"\033[90m--> {Colors.RESET + Colors.BOLD}{userRoleColor(user)}{user}{RESET} uses /help{RESET + Colors.RESET}")
                    client.send(
                        f"""{GREEN +  Colors.UNDERLINE + Colors.BOLD}Default commands{RESET + Colors.RESET}
        {BLUE + Colors.BOLD}/help: {RESET}Help Command
        {BLUE + Colors.BOLD}/about: {RESET}About {chat_name}
        {BLUE + Colors.BOLD}/news: {RESET}Newsletter{RESET + Colors.RESET}
        {BLUE + Colors.BOLD}/exit, /quit: {RESET}Leave chat
        {BLUE + Colors.BOLD}/clientinfo: {RESET}Get some information about you{RESET + Colors.RESET}
        {BLUE + Colors.BOLD}/shrug: {RESET}¯\_(ツ)_/¯
        {BLUE + Colors.BOLD}/tableflip: {RESET}(╯°□°)╯︵ ┻━┻
        {BLUE + Colors.BOLD}/unflip: {RESET}┬─┬ノ( º _ ºノ){RESET + Colors.RESET}
        """.encode("utf-8"))
                    
                    time.sleep(0.1)
                    client.send(
                        f"""{CYAN + Colors.UNDERLINE + Colors.BOLD}Profile & User Commands{RESET + Colors.RESET}
        {BLUE + Colors.BOLD}/online: {RESET}Shows online users
        {BLUE + Colors.BOLD}/members, /users: {RESET}Shows registered users
        {BLUE + Colors.BOLD}/userinfo, /user, /member <user>/me: {RESET}Shows information about the specified user
        {BLUE + Colors.BOLD}/nick <nickname/remove>: {RESET}Changes nickname to <nickname> or removes it
        {BLUE + Colors.BOLD}/description <desc>: {RESET}Set your user description{RESET + Colors.RESET}
        {BLUE + Colors.BOLD}/badge set <badge>: {RESET}Sets your main badge
        {BLUE + Colors.BOLD}/discord <discord_uname>: {RESET}Set your discord username{RESET + Colors.RESET}
        {BLUE + Colors.BOLD}/afk: {RESET}Toggle afk status
        {BLUE + Colors.BOLD}/unafk: {RESET}Untoggle afk status
        {BLUE + Colors.BOLD}/afks, /afklist: {RESET}Shows afk users
        """.encode("utf-8"))
                    
                    time.sleep(0.1)
                    client.send(
                        f"""{MAGENTA +  Colors.UNDERLINE + Colors.BOLD}Admin commands{RESET + Colors.RESET}
        {BLUE + Colors.BOLD}/ban <user>: {RESET}Bans the specificed user{RESET + Colors.RESET}
        {BLUE + Colors.BOLD}/unban <user>: {RESET}Unbans the specificed user{RESET + Colors.RESET}        
        {BLUE + Colors.BOLD}/mute <user>: {RESET}Mutes the specificed user{RESET + Colors.RESET}
        {BLUE + Colors.BOLD}/unmute <user>: {RESET}Unmutes the specificed user{RESET + Colors.RESET}
        {BLUE + Colors.BOLD}/broadcast <message>: {RESET}Broadcast a message{RESET + Colors.RESET}
        {BLUE + Colors.BOLD}/role get/set <user> (<role>) [<color>]: {RESET}Gets or sets the role of a user{RESET + Colors.RESET}
        {BLUE + Colors.BOLD}/role color <user> <color>: {RESET}Gets or sets the role of a user{RESET + Colors.RESET}
        {BLUE + Colors.BOLD}/badge set <badge> <user>: {RESET}Changes main badge of <user> to <badge>
        {BLUE + Colors.BOLD}/badge add <badge> (<user>): {RESET}Adds new badge to your profile or to <user>'s profile
        {BLUE + Colors.BOLD}/bwords set/get <user> (<true/false>): {RESET}Enable or disable whether a user should be affected by the bad words{RESET + Colors.RESET}
        {BLUE + Colors.BOLD}/bwords reload: {RESET}Reloads all blacklisted words{RESET + Colors.RESET}
        {BLUE + Colors.BOLD}/bwords add <word>: {RESET}Adds a blacklisted word{RESET + Colors.RESET}
        {BLUE + Colors.BOLD}/debug: {RESET}View debug informations{RESET + Colors.RESET}
        {BLUE + Colors.BOLD}/kickall: {RESET}Kick all users (Currently not working){RESET + Colors.RESET}
        """.encode("utf8"))
                    
                    
                # Online Command
                case "/online":
                    onlineUsers = ', '.join([user for user in sorted(users.values())])
                    onlineUsersLen2 = len([user for user in sorted(users.values())])
                    client.send(f"""{GREEN +  Colors.UNDERLINE + Colors.BOLD}Users who are currently online ({onlineUsersLen2}){RESET + Colors.RESET}
        {Colors.BOLD}->{Colors.RESET} {CYAN}{onlineUsers}{RESET + Colors.RESET}""".encode("utf8"))
                
                
                # Afk Command
                case "/afk":
                    if user in afks:
                        client.send(f"{YELLOW + Colors.BOLD}You are already AFK!{RESET + Colors.RESET}".encode("utf8"))
                        
                    else:
                        broadcast(f"{user} is now AFK 🌙..")
                        afks.append(user)
                
                
                # Unafk Comamnd
                case "/unafk":
                    if user not in afks:
                        client.send(f"{YELLOW + Colors.BOLD}You are not AFK!{RESET + Colors.RESET}".encode("utf8"))
                    
                    else:
                        broadcast(f"{user} is no longer AFK 🌻!")
                        afks.remove(user)
                    
                    
                # Whois Afk Command
                case "/afks" | "/afklist":
                    afkUsers = ', '.join([afks for afks in sorted(afks)])
                    afkUsersLen = len([afks for afks in sorted(afks)])
                    client.send(f"""{GREEN +  Colors.UNDERLINE + Colors.BOLD}Users who are currently Afk ({afkUsersLen}){RESET + Colors.RESET}
        {Colors.BOLD}->{Colors.RESET} {CYAN}{afkUsers}{RESET}""".encode("utf8"))
                
                
                # Debug Command
                case "/debug":
                    try: 
                        c.execute('SELECT role FROM users WHERE username = ?', (user,))
                        
                    except Exception as e:
                        sqlError(e)
                        
                    res = c.fetchone()
                    
                    if res[0] == "admin":
                        client.send(f"""Client Object: {client}
        IP Object: {addresses[client]}
        User Object: {users[client]}
        Addresses: {addresses}
        Users: {users}""".encode("utf8"))
                        
                    else:
                        client.send(f"{RED}Sorry, you do not have permissons for that.{RESET}".encode("utf8"))
                                
                                                
                # Kickall Command
                case "/kickall":
                    try: 
                        c.execute('SELECT role FROM users WHERE username = ?', (user,))
                        
                    except Exception as e:
                        sqlError(e)
                        
                    res = c.fetchone()
                    
                    if res[0] == "admin":
                        cleanup()
                        
                    else:
                        client.send(f"{RED}Sorry, you do not have permissons for that.{RESET}".encode("utf8"))
                
                
                # Shrug Command
                case "/shrug":
                    broadcast("¯\_(ツ)_/¯", user)
                
                
                # Tableflip Command
                case "/tableflip":
                    broadcast("(╯°□°)╯︵ ┻━┻", user)
                
                
                # Unflip Command
                case "/unflip":
                    broadcast("┬─┬ノ( º _ ºノ)", user)
                
                
                # About Command
                case "/about":
                    client.send(
                        f"""{GREEN +  Colors.UNDERLINE + Colors.BOLD}About {chat_name}{RESET + Colors.RESET}
        {BLUE + Colors.BOLD}Thank you for using {chat_name}!{RESET}
        {BLUE + Colors.BOLD}Version: {RESET}{short_ver} {codename} ({server_edition})
        {BLUE + Colors.BOLD}Author: {RESET}Juliandev02{RESET + Colors.RESET}"""
        .encode("utf8"))
                    
                    
                # News Command
                case "/news":
                    client.send(news.encode("utf8"))
                
                
                # Clientinfo Command
                case "/clientinfo":
                    client.send(f"{addresses[client]}".encode("utf8"))
                    time.sleep(0.1)
                    client.send(f"{users[client]}".encode("utf8"))
                    time.sleep(0.1)
                    client.send(f"{client}".encode("utf8"))
                    
                
                # Member Command
                case "/members" | "/users":
                    c.execute("SELECT username FROM users")
                    raw_members = c.fetchall()
                    membersLen = len([raw_members for raw_members in sorted(raw_members)])
                    members = ", ".join([result[0] for result in raw_members])

                    client.send(f"""{CYAN +  Colors.UNDERLINE + Colors.BOLD}Members on this server ({membersLen}){RESET + Colors.RESET}
        {Colors.BOLD}->{Colors.RESET} {CYAN}{members}{RESET}""".encode("utf8"))
                
                
                # Show Description Command
                case "/description" | "/desc":
                    c.execute("SELECT description FROM users WHERE username = ?", (user,))
                    desc = c.fetchone()[0]
                    client.send(f"{LIGHTGREEN_EX + Colors.BOLD}Your current description: {RESET}{desc}{Colors.RESET}".encode("utf8"))
                
                
                # Delete Account Command
                case "/deleteaccount":
                    client.send(f"{YELLOW + Colors.BOLD}Are you sure you want to delete your user account? This action is irreversible!!{RESET + Colors.RESET}".encode("utf8"))
                    confirmDelete1 = client.recv(2048).decode("utf8")
                    
                    if confirmDelete1.lower() == "yes":
                        client.send(f"{RED + Colors.BOLD}THIS IS YOUR VERY LAST WARNING! This action is irreversible!! ARE YOU SURE?{RESET + Colors.RESET}".encode("utf8"))
                        confirmDelete2 = client.recv(2048).decode("utf8")
                        
                        if confirmDelete2.lower() == "yes":
                            client.send(f"{YELLOW + Colors.BOLD}Enter your username to confirm the deletion of your account:{RESET + Colors.RESET}".encode("utf8"))
                            confirmUsernameDelete = client.recv(2048).decode("utf8")
                            
                            if confirmUsernameDelete == user:
                                client.send(f"{YELLOW + Colors.BOLD}Deleting your user account...{RESET + Colors.RESET}".encode("utf8"))
                                
                                try:
                                    cursor = db.cursor()
                                    cursor.execute("DELETE FROM users WHERE username = ?", (user,))
                                    db.commit()
                                    client.send(f"{GREEN + Colors.BOLD}Deleted{RESET + Colors.RESET}".encode("utf8"))
                                    client.close()
                                    sys.exit(1)
                                    
                                except Exception as e:
                                    log.error(e)
                                    
                            else: 
                                client.send(f"{YELLOW + Colors.BOLD}Deletion of your account has been canceled...{RESET + Colors.RESET}".encode("utf8"))
                        else:
                            client.send(f"{YELLOW + Colors.BOLD}Deletion of your account has been canceled...{RESET + Colors.RESET}".encode("utf8"))
                    else:
                        client.send(f"{YELLOW + Colors.BOLD}Deletion of your account has been canceled...{RESET + Colors.RESET}".encode("utf8"))

            
                case "/":
                    client.send(f"{GREEN + Colors.BOLD}Need help? Take a look at our help command! /help{RESET + Colors.RESET}".encode("utf8"))
                
                
                case _:
                    
                    if user in afks:
                        client.send(f"{RED}Sorry, you are AFK.{RESET}".encode("utf8"))
                        
                    elif isMuted(user) == True:
                        client.send(f"{RED + Colors.BOLD}Sorry, but you were muted by an administrator. Please contact him/her if you have done nothing wrong, or wait until you are unmuted.{RESET + Colors.RESET}".encode("utf8"))
                    
                    elif isAccountEnabled(user) == False:
                        client.send(f"{RED + Colors.BOLD}Your account was disabled by an administrator.{RESET + Colors.RESET}".encode("utf8"))
                        
                    else:
                        if enable_messages == True:
                            log.info(f"{user} ({address}): {message}")
                                
                        broadcast(message, user)
                
            
                
        except Exception as e:
            log.error("A client-side error occurred.")
            
            debugLogger(e, "004")
            log.info(f"[<] {user} ({address}) has left")
            
            del addresses[client]
            del users[client]
            client.close()
            
            broadcast(f"{YELLOW + Colors.BOLD}<- {userRoleColor(user)}{user}{YELLOW + Colors.BOLD} has left the chat.{RESET + Colors.RESET}")
            break


def clientLogin(client):
    def register():
        global db
        global c
        
        client.send(f"{MAGENTA + Colors.BOLD + Colors.UNDERLINE}Welcome!{RESET + Colors.RESET}\n        {Colors.BOLD}Register, to chat with us!{Colors.RESET}".encode("utf8"))
    
        time.sleep(0.05)
        client.send(f"{GREEN + Colors.BOLD}Username: {RESET + Colors.RESET}".encode("utf8"))
        registeredUsername = client.recv(2048).decode("utf8")
        
        if registeredUsername.lower() == "exit":
            client.close()
            sys.exit()
        
        for uname in registeredUsername.split():
            uname = uname.lower()
            
            if uname in blacklist:
                client.send(f"{YELLOW + Colors.BOLD}This username is not allowed{RESET + Colors.RESET}".encode("utf8"))    
                client.close()
                sys.exit()
        try:
            c.execute("SELECT username FROM users WHERE username = ? ", (registeredUsername,))
            
            usedUsernames = c.fetchall()[0]
            usedUsernames = "".join(usedUsernames)
            
            
            if usedUsernames == usedUsernames:
                client.send(f"{YELLOW + Colors.BOLD}This username is already in use!{RESET + Colors.RESET}".encode("utf8"))    
                register()
            
        except:
            pass
            

            
        client.send(f"{GREEN + Colors.BOLD}Password: {RESET + Colors.RESET}".encode("utf8"))
        registeredPassword = client.recv(2048).decode("utf8")
        
        client.send(f"{GREEN + Colors.BOLD}Confirm Password: {RESET + Colors.RESET}".encode("utf8"))
        confirmPassword = client.recv(2048).decode("utf8")
        
        if registeredPassword != confirmPassword:
            client.send(f"{RED + Colors.BOLD}Passwords do not match{RESET + Colors.RESET}".encode("utf8"))
            register()
        
        client.send(f"{GREEN + Colors.BOLD}Role Color (Red, Green, Cyan, Blue, Yellow, Magenta): {RESET + Colors.RESET}".encode("utf8"))
        registeredRoleColor = client.recv(2048).decode("utf8")

        client.send(f"{YELLOW + Colors.BOLD}Are you sure? Changing the username is currently not possible and requires a lot of time.{RESET + Colors.RESET}".encode("utf8"))
        confirmUsername = client.recv(2048).decode("utf8")
        
        if confirmUsername == "yes":
            client.send(f"{YELLOW + Colors.BOLD}Processing... {RESET + Colors.RESET}".encode("utf8"))
            
            try:
                db = sql.connect(server_dir + "/users.db", check_same_thread=False)
                c = db.cursor()
                
                client.send(f"{GREEN + Colors.BOLD}Creating your User account... {RESET + Colors.RESET}".encode("utf8"))
                
                c.execute('INSERT INTO users (username, password, role, role_color, enableBlacklistedWords, accountEnabled, muted) VALUES (?, ?, "member", ?, "true", "true", "false")', (registeredUsername, registeredPassword, registeredRoleColor.lower()))
                db.commit()
                db.close()
                
                client.send(f"{GREEN + Colors.BOLD}Created!{RESET + Colors.RESET}".encode("utf8"))
                client.close()
                sys.exit(1)
                
            except Exception as e:
                sqlError(e)
            
        else:
            client.send(f"{RED + Colors.BOLD}Registration has been canceled. Start from the beginning...{RESET + Colors.RESET}".encode("utf8"))
            time.sleep(0.5)
            register()
            
        
    client.send(f"{Colors.BOLD}Welcome to Strawberry Chat!{Colors.RESET}".encode("utf8"))
    client.send(f"{Colors.BOLD}New here? Type '{MAGENTA}Register{RESET}' to register! You want to leave? Type '{MAGENTA}Exit{RESET}' {Colors.RESET}".encode("utf8"))
    client.send(f"".encode("utf8"))
    
    time.sleep(0.1)
    client.send(f"{GREEN + Colors.BOLD}Username: {RESET + Colors.RESET}".encode("utf8"))
    username = client.recv(2048).decode("utf8")
    
    if username.lower() == "register":
        register()
        
    elif username.lower() == "exit":
        client.close()
        sys.exit()
        
    time.sleep(0.01)
    
    client.send(f"{GREEN + Colors.BOLD}Password: {RESET + Colors.RESET}".encode("utf8"))
    password = client.recv(2048).decode("utf8")

    try: 
        c.execute('SELECT * FROM users WHERE username = ? AND password = ? AND accountEnabled = ?', (username, password, "true"))
        
    except Exception as e:
        log.error(f"A login-error occurred")
        debugLogger(e, "002")
        
    res = c.fetchall()
    
    if res:
        c.execute('SELECT username FROM users WHERE username = ? AND password = ?', (username, password))
        result = c.fetchone()
        
        if result is not None:
            nickname = result[0]      
            return nickname
    

    else:   
        alreadyTaken = True
        while alreadyTaken:
            try:
                enabled = c.execute('SELECT accountEnabled FROM users WHERE username = ? AND password = ?', (username, password))
                enabled = str(enabled.fetchone()[0])
                
            except TypeError:
                pass

            if enabled == "false":
                client.send(f"{RED + Colors.BOLD}Your account was disabled by an administrator.{RESET + Colors.RESET}".encode("utf8"))
                client.recv(2048).decode("utf8")
                client.close()
            
            client.send(f"{RED + Colors.BOLD}Wrong username or password.{RESET + Colors.RESET}".encode("utf8"))
            client.send(f"{GREEN + Colors.BOLD}Username: {RESET + Colors.RESET}".encode("utf8"))
            username = client.recv(2048).decode("utf8")
            time.sleep(0.01)
            
            if username.lower() == "register":
                register()
                
            elif username.lower() == "exit":
                client.close()
                sys.exit()
            
            client.send(f"{GREEN + Colors.BOLD}Password: {RESET + Colors.RESET}".encode("utf8"))
            password = client.recv(2048).decode("utf8")
            time.sleep(0.01)
            
            try: 
                c.execute('SELECT * FROM users WHERE username = ? AND password = ? AND accountEnabled = ?', (username, password, "true"))
                
            except Exception as e:
                log.error(f"An error occurred.")
                debugLogger(e, "100")
                
            res = c.fetchall()
            
            if res:
                c.execute('SELECT username FROM users WHERE username = ? AND password = ?', (username, password))
                result = c.fetchone()
                
                if result is not None:
                    nickname = result[0]
                    alreadyTaken = False
                    return nickname
                
            else: alreadyTaken = True


 
def broadcast(message, sentBy=""):
    def userRoleColor(uname):
        db = sql.connect(server_dir + "/users.db", check_same_thread=False)
        c = db.cursor()
        c.execute('SELECT role_color FROM users WHERE username = ?', (uname,))
        color = c.fetchone()
        db.close()
        
        if color[0] is not None: 
            match color[0]:
                case "red": 
                    return RED
                
                case "green": 
                    return GREEN
                    
                case "cyan": 
                    return CYAN
                
                case "blue": 
                    return BLUE

                case "yellow": 
                    return YELLOW
                 
                case "magenta": 
                    return MAGENTA
                
                case "lightred":
                    return LIGHTRED_EX
                
                case "lightgreen":
                    return LIGHTGREEN_EX
                
                case "lightcyan":
                    return LIGHTCYAN_EX
                
                case "lightblue":
                    return LIGHTBLUE_EX

                case "lightyellow":
                    return LIGHTYELLOW_EX

                case "lightmagenta":
                    return LIGHTMAGENTA_EX
                
                case "boldred":
                    return Colors.BOLD + RED

                case "boldgreen":
                    return Colors.BOLD + GREEN
                
                case "boldcyan":
                    return Colors.BOLD + CYAN
                
                case "boldblue":
                    return Colors.BOLD + BLUE
                
                case "boldyellow":
                    return Colors.BOLD + YELLOW
                
                case "boldmagenta":
                    return Colors.BOLD + MAGENTA
                
                case _:
                    return RESET
        else: 
            return RESET
        
                
        
    try:
        if sentBy == "":
            for user in users:
                user.send(message.encode("utf8"))

        else:
            for user in users:
                try: 
                    c.execute('SELECT badge FROM users WHERE username = ?', (sentBy,))
                    res = c.fetchone()
               
                    if res[0] is not None:
                        badge = " [" + res[0] + "]"
                        
                    else:
                        badge = ""
                        
                except Exception as e:
                    log.error("Something went wrong while... doing something with the badges?: " + e)
                
                if hasNickname(sentBy) == True:
                    user.send(f"{userRoleColor(sentBy)}{userNickname(sentBy)} (@{sentBy.lower()}){badge}{RESET + Colors.RESET}: {message}".encode("utf8"))
                    
                else: 
                    user.send(f"{userRoleColor(sentBy)}{sentBy}{badge}{RESET + Colors.RESET}: {message}".encode("utf8"))
                
    except IOError as e:
        if e.errno == errno.EPIPE:
            log.critical(f"Broken Pipe Error. You may need to restart your server!! DO NOT EXIT THE CHAT CLIENT WITH ^C!!!")
            debugLogger(e, "122")
            exit(1)
  
    except Exception as e:
        log.error(f"A broadcasting error occurred.")
        debugLogger(e, "003")
        exit(1)



def cleanup():
    if len(addresses) != 0:
        for sock in addresses.keys():
            sock.close()
    print(f"{YELLOW + Colors.BOLD}Runtime has stopped.{RESET + Colors.RESET}")


def main():
    try:
        atexit.register(cleanup)

        socketFamily = socket.AF_INET
        socketType = socket.SOCK_STREAM
        serverSocket = socket.socket(socketFamily, socketType)
        serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        serverSocket.bind((ipaddr, port))
        serverSocket.listen()

        print(f"{GREEN + Colors.BOLD}* -- Server started -- *{RESET + Colors.RESET}")
        print(f"{CYAN + Colors.BOLD}{chat_name} v{short_ver} {codename} ({server_edition}){RESET + Colors.RESET}")

        if enable_messages == True:
            print(f"{YELLOW + Colors.BOLD}[!] Enabled Flag {CYAN}'enable-messages'{RESET + Colors.RESET}")
        
        if debug_mode:
            print(f"{YELLOW + Colors.BOLD}[!] Enabled debug mode for debugging{RESET + Colors.RESET}")
            
        print(f"{YELLOW + Colors.BOLD}>>> {RESET}Server is running on {ipaddr}:{port}")

        connThread = threading.Thread(target=connectionThread, args=(serverSocket,))
        connThread.start()
        connThread.join()

        cleanup()
        serverSocket.close()
        log.info("Server stopped")
        print("Server has shut down.")
        
    except KeyboardInterrupt: 
        exit()
    

users = {}
addresses = {}

if __name__ == "__main__":
    main()
    db.close()
    pass
