import socket
import threading

import os
import sys
import logging
import sqlite3 as sql
import argon2

import yaml
from yaml import SafeLoader

import atexit
import datetime
import time
import errno
import random
import requests
import re
import json

from colorama import Fore, Style
from .colors import *
from init import *
from .vars import table_query


func_db = sql.connect(server_dir + "/users.db", check_same_thread=False)

# Removed ansi characters
def escape_ansi(string):
    ansi_escape = re.compile(r'(?:\x1B[@-_]|[\x80-\x9F])[0-?]*[ -/]*[@-~]')
    return ansi_escape.sub('', string)

def escape_htpf(string):
    to_ret = string \
            .replace("#red", "") \
            .replace("#green", "") \
            .replace("#yellow", "") \
            .replace("#blue", "") \
            .replace("#magenta", "") \
            .replace("#cyan", "") \
            .replace("#white", "") \
            .replace("#reset", "") \
            .replace("#bold", "") \
            .replace("#underline", "")
                
    return to_ret

def replace_htpf(string, reset_color: bool = False):
    to_ret = string \
            .replace("#red", RED) \
            .replace("#green", GREEN) \
            .replace("#yellow", YELLOW) \
            .replace("#blue", BLUE) \
            .replace("#magenta", MAGENTA) \
            .replace("#cyan", CYAN) \
            .replace("#white", WHITE) \
            .replace("#reset", RESET) \
            .replace("#bold", Colors.BOLD) \
            .replace("#underline", Colors.UNDERLINE) \
            .replace("#today", datetime.datetime.today().strftime("%Y-%m-%d")) \
            .replace("#curtime", datetime.datetime.now().strftime("%H:%M")) \
            .replace("#month", datetime.datetime.today().strftime("%m")) \
            .replace("#fullmonth", datetime.datetime.now().strftime("%h")) \
            .replace("#ftoday", datetime.datetime.now().strftime("%A, %d. %h %Y")) \
            .replace("#tomorrow", (datetime.date.today() + datetime.timedelta(days=1)).strftime("%Y-%m-%d")) \
            .replace("#ftomorrow", (datetime.date.today() + datetime.timedelta(days=1)).strftime("%A, %d. %h %Y"))
    
    if reset_color:
        return to_ret + RESET + Colors.RESET
    
    return to_ret

def input_regen_database(type: str = "standard"):
    if type == "standard":
        confirm_input = input(f"{YELLOW + Colors.BOLD}>>> {RESET}WARNING: This will delete your database! Are you sure?: ")
        
        if confirm_input.lower() == "yes": regen_database(call_exit=True)
        else: print(f"{Colors.GRAY + Colors.BOLD}>>> {RESET + Colors.RESET + Colors.BOLD}Cancelled database regeneration process")
        
    elif type == "corrupted":
        confirm_input = input(f"{YELLOW + Colors.BOLD}>>> {RESET}WARNING: Your database is corrupted or was not generated correctly.\n    Would you like to regenerate your database? (Not regenerating the database leads to incorrect execution of the program) ")
        
        if confirm_input.lower() == "yes": regen_database(call_exit=True)
        else: print(f"{Colors.GRAY + Colors.BOLD}>>> {RESET + Colors.RESET + Colors.BOLD}Cancelled database regeneration process")

def regen_database(call_exit: bool = False):
    os.remove(server_dir + "/users.db")
    db = sql.connect(server_dir + "/users.db", check_same_thread=False)
    cr_cursor = db.cursor()
    print(f"{GREEN + Colors.BOLD}>>> {RESET}Created database")

    cr_cursor.execute(table_query)
    db.commit()
    cr_cursor.close()
    print(f"{GREEN + Colors.BOLD}>>> {RESET}Created table")
    
    if call_exit:
        print(f"{YELLOW + Colors.BOLD}>>> {RESET}Restart your server to connect to your new database.")
        exit()

def table_exists(table_name, cursor):
    cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
    return cursor.fetchone() is not None

def create_empty_file(filename):
    with open(server_dir + "/" + filename, "w") as ef:
        pass
    
def send_json(data):
    return json.dumps(data)

def broadcast_all(message, format: StbCom = StbCom.PLAIN):
    try:
        for user in users:
            try:
                json_builder = {
                    "message_type": StbCom.SYS_MSG,
                    "message": {
                        "content": message
                    }
                }
                user.send(send_json(json_builder).encode("utf8"))
                
            except BrokenPipeError as e:
                debug_logger(e, stbexceptions.broken_pipe_warning, type=StbTypes.WARNING)
                log.warning("You should kick some invalid sessions.")

    except Exception as e:
        log.error(f"A broadcasting error occurred.")
        debug_logger(e, stbexceptions.communication_error)

# Check if user has a nickname
def hasNickname(uname):
    db = sql.connect(server_dir + "/users.db", check_same_thread=False)
    c = db.cursor()
    c.execute('SELECT nickname FROM users WHERE LOWER(username) = ?', (uname.lower(),))
    unick = c.fetchone()
    c.close()
    
    if unick[0] is not None:  return True
    else: return False

# Check if user has a (main) badge
def hasBadge(uname):
    db = sql.connect(server_dir + "/users.db", check_same_thread=False)
    c = db.cursor()
    c.execute('SELECT badge FROM users WHERE LOWER(username) = ?', (uname.lower(),))
    unick = c.fetchone()
    c.close()
    
    if unick[0] is not None: return True
    else: return False
    
# Print a proper user name information for memberlist command
def memberListNickname(uname):
    db = sql.connect(server_dir + "/users.db", check_same_thread=False)
    c = db.cursor()
    c.execute("SELECT nickname FROM users WHERE LOWER(username) = ?", (uname.lower(),))
    nickname = c.fetchone()
    c.close()
    
    if hasNickname(uname): return f"{nickname[0]} (@{uname.lower()})"
    else: return uname

def memberListBadge(uname):
    db = sql.connect(server_dir + "/users.db", check_same_thread=False)
    c = db.cursor()
    c.execute("SELECT badge FROM users WHERE LOWER(username) = ?", (uname.lower(),))
    badge = c.fetchone()
    c.close()
    
    if hasBadge(uname): return f"[{badge[0]}]"
    else: return ""
    
# Get user role color from the user
def userRoleColor(uname):
    db = sql.connect(server_dir + "/users.db", check_same_thread=False)
    c = db.cursor()
    c.execute('SELECT role_color FROM users WHERE LOWER(username) = LOWER(?)', (uname,))
    color = c.fetchone()
    c.close()
    
    if color[0] is not None: 
        match color[0]:
            case "red": return RED + Colors.BOLD
            case "green": return GREEN + Colors.BOLD
            case "cyan": return CYAN + Colors.BOLD
            case "blue": return BLUE
            case "yellow": return YELLOW
            case "magenta": return MAGENTA
            case "lightred": return LIGHTRED_EX
            case "lightgreen": return LIGHTGREEN_EX
            case "lightcyan": return LIGHTCYAN_EX
            case "lightblue": return LIGHTBLUE_EX
            case "lightyellow": return LIGHTYELLOW_EX
            case "lightmagenta": return LIGHTMAGENTA_EX
            case "boldred": return Colors.BOLD + RED
            case "boldgreen": return Colors.BOLD + GREEN
            case "boldcyan": return Colors.BOLD + CYAN
            case "boldblue": return Colors.BOLD + BLUE
            case "boldyellow": return Colors.BOLD + YELLOW            
            case "boldmagenta": return Colors.BOLD + MAGENTA
            case _: return RESET
    else: return RESET
    
def isOnline(uname):
    if uname in users.values():
        if uname in afks: return "🌙"
        else: return "🟢"
    
    else: return f"{Colors.GRAY}〇{RESET}"
    
def contains_whitespace(string):
    for c in string:
        if c == " ":
            return True
    return False
    
def check_user_status(type="object", user = None):
    if type == "object":
        user_status = user.status()
        
    elif type == "name":
        _user = User(socket="type.none")
        _user.set_username(user)
            
        user_status = _user.get_status()
    
    match user_status:
        case User.Status.online: return "🟢"
        case User.Status.afk: return "🌙"
        case User.Status.dnd: return "🔴"
        case User.Status.offline: return f"{Colors.GRAY}〇{RESET}"

# Check if a user exists
def doesUserExist(uname):
    db = sql.connect(server_dir + "/users.db", check_same_thread=False)
    c = db.cursor()
    uname = uname.lower()
    c.execute('SELECT username FROM users WHERE LOWER(username) = ?', (uname,))
    
    try:
        userExists = c.fetchone()[0]
        
    except:
        return False
    
    if userExists.lower() == uname:
        return True
    
    c.close()

def hash_password(password):
    ph = argon2.PasswordHasher()
    return ph.hash(password)

def verify_password(stored_password, entered_password):
    ph = argon2.PasswordHasher()
    
    try:
        ph.verify(stored_password, entered_password)
        return True
    
    except argon2.exceptions.VerifyMismatchError:
        return False

def is_empty_or_whitespace(string): return all(char.isspace() for char in string)

# Get user's nickname
def userNickname(uname):
    db = sql.connect(server_dir + "/users.db", check_same_thread=False)
    c = db.cursor()
    c.execute('SELECT nickname FROM users WHERE LOWER(username) = LOWER(?)', (uname,))
    unick = c.fetchone()
    c.close()
    
    if unick[0] is not None: 
        unick = unick[0]
        return unick
    
    else:
        return uname

# Get user's nickname
def userAvatarUrl(uname):
    db = sql.connect(server_dir + "/users.db", check_same_thread=False)
    c = db.cursor()
    c.execute('SELECT avatar_url FROM users WHERE LOWER(username) = ?', (uname.lower(),))
    avatar_url = c.fetchone()
    c.close()
    
    if avatar_url[0] is not None: 
        avatar_url = avatar_url[0]
        return avatar_url
    
    else:
        return avatar_url

# Check if user is muted
def isMuted(uname):
    c = func_db.cursor()
    c.execute('SELECT muted FROM users WHERE LOWER(username) = ?', (uname.lower(),))
    mutedStatus = c.fetchone()
    c.close()
    
    if mutedStatus[0] == "true": return True
    else: return False
    
# Check if user's account is enabled
def isAccountEnabled(uname):
    c = func_db.cursor()
    c.execute('SELECT account_enabled FROM users WHERE LOWER(username) = ?', (uname.lower(),))
    accountEnabledStatus = c.fetchone()
    c.close()
    
    if accountEnabledStatus[0] == "true": return True
    else:  return False
    
# Blacklisted word functions
def open_blacklist():
    with open(server_dir + "/blacklist.txt", "r") as f:
        for word in f:
            word = word.strip().lower()
            blacklist.add(word)
            
# example: user = Julian (person that you want to send an dm)
#          user_check = Juliandev02 (check if this person (juliandev02) is blocked by julian)
def is_blocked(user: str, user_check: str):
    cmd_db.execute("SELECT blocked_users FROM users WHERE LOWER(username) = ?", (user.lower(),))
    blocked_users = cmd_db.fetchall()
    
    if blocked_users[0][0] == None:
        return False
        
    blocked_users = blocked_users[0][0].split(",")
    
    if user_check.lower() in blocked_users:
        return True
    
    return False