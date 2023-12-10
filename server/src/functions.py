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

from colorama import Fore, Style
from .colors import *
from init import *
from .vars import table_query

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

def repl_htpf(string):
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
                
    return to_ret

def regen_database():
    os.remove(server_dir + "/users.db")
    db = sql.connect(server_dir + "/users.db", check_same_thread=False)
    cr_cursor = db.cursor()
    print(f"{GREEN + Colors.BOLD}>>> {RESET}Created database")

    cr_cursor.execute(table_query)
    db.commit()
    cr_cursor.close()

def create_empty_file(filename):
    with open(server_dir + "/" + filename, "w") as ef:
        pass
    
def broadcast_all(message):
    try:
        for user in users:
            user.send(message.encode("utf8"))
    
    except BrokenPipeError as e:
        debug_logger(e, stbexceptions.broken_pipe_warning, type=StbTypes.WARNING)
        log.warning("You should kick some invalid sessions.")
    
    except IOError as e:
        if e.errno == errno.EPIPE:
            pass
  
    except Exception as e:
        pass
        
# Check if user has a nickname
def hasNickname(uname):
    db = sql.connect(server_dir + "/users.db", check_same_thread=False)
    c = db.cursor()
    c.execute('SELECT nickname FROM users WHERE username = ?', (uname,))
    unick = c.fetchone()
    c.close()
    
    if unick[0] is not None: 
        return True
    
    else: 
        return False

# Check if user has a (main) badge
def hasBadge(uname):
    db = sql.connect(server_dir + "/users.db", check_same_thread=False)
    c = db.cursor()
    c.execute('SELECT badge FROM users WHERE username = ?', (uname,))
    unick = c.fetchone()
    c.close()
    
    if unick[0] is not None: 
        return True
    
    else: 
        return False
    
# Print a proper user name information for memberlist command
def memberListNickname(uname):
    db = sql.connect(server_dir + "/users.db", check_same_thread=False)
    c = db.cursor()
    c.execute("SELECT nickname FROM users WHERE username = ?", (uname,))
    nickname = c.fetchone()
    c.close()
    
    if hasNickname(uname):
        return f"{nickname[0]} (@{uname.lower()})"
    
    else:
        return uname

def memberListBadge(uname):
    db = sql.connect(server_dir + "/users.db", check_same_thread=False)
    c = db.cursor()
    c.execute("SELECT badge FROM users WHERE username = ?", (uname,))
    badge = c.fetchone()
    c.close()
    
    if hasBadge(uname):
        return f"[{badge[0]}]"
    
    else:
        return ""
    
# Get user role color from the user
def userRoleColor(uname):
    db = sql.connect(server_dir + "/users.db", check_same_thread=False)
    c = db.cursor()
    c.execute('SELECT role_color FROM users WHERE username = ?', (uname,))
    color = c.fetchone()
    c.close()
    
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
    
def isOnline(uname):
    if uname in users.values():
        if uname in afks:
            return "🌙"
        
        else:
            return "🟢"
    
    else:
        return f"{Colors.GRAY}〇{RESET}"

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
    hashed_password = ph.hash(password)
    
    return hashed_password

def verify_password(stored_password, entered_password):
    ph = argon2.PasswordHasher()
    
    try:
        ph.verify(stored_password, entered_password)
        return True
    
    except argon2.exceptions.VerifyMismatchError:
        return False

def is_empty_or_whitespace(string):
    return all(char.isspace() for char in string)

# Blacklisted word functions
def open_blacklist():
    with open(server_dir + "/blacklist.txt", "r") as f:
        for word in f:
            word = word.strip().lower()
            blacklist.add(word)