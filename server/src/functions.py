import socket
import threading

import os
import sys
import logging
import sqlite3 as sql

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
def escape_ansi(line):
    ansi_escape = re.compile(r'(?:\x1B[@-_]|[\x80-\x9F])[0-?]*[ -/]*[@-~]')
    return ansi_escape.sub('', line)

def repl_htpf(str):
    to_ret = str \
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
                
    except IOError as e:
        if e.errno == errno.EPIPE:
            # log.critical(f"Broken Pipe Error. You may need to restart your server!! DO NOT EXIT THE CHAT CLIENT WITH ^C!!!")
            # debugLogger(e, "122")
            print(e)
            exit(1)
  
    except Exception as e:
        # log.error(f"A broadcasting error occurred.")
        # debugLogger(e, "003")
        print(e)
        exit(1)