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
from init import server_dir
from .vars import table_query

# Receive your global ip address for verification
def get_global_ip():
    response = requests.get('https://api.ipify.org?format=json')
    data = response.json()
    return data['ip']

# Removed ansi characters
def escape_ansi(line):
    ansi_escape = re.compile(r'(?:\x1B[@-_]|[\x80-\x9F])[0-?]*[ -/]*[@-~]')
    return ansi_escape.sub('', line)

def repl_htpf(str):
    to_ret = str.replace("#red", RED
                ).replace("#green", GREEN
                ).replace("#yellow", YELLOW
                ).replace("#blue", BLUE
                ).replace("#magenta", MAGENTA
                ).replace("#cyan", CYAN
                ).replace("#white", WHITE
                ).replace("#reset", RESET
                ).replace("#bold", Colors.BOLD
                ).replace("#underline", Colors.UNDERLINE
                ).replace("#today", datetime.datetime.today().strftime("%Y-%m-%d")
                ).replace("#curtime", datetime.datetime.now().strftime("%H:%M")
                ).replace("#month", datetime.datetime.today().strftime("%m")
                ).replace("#fullmonth", datetime.datetime.now().strftime("%h")
                ).replace("#ftoday", datetime.datetime.now().strftime("%A, %d. %h %Y")
                ).replace("#tomorrow", (datetime.date.today() + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
                ).replace("#ftomorrow", (datetime.date.today() + datetime.timedelta(days=1)).strftime("%A, %d. %h %Y")
                )
                
    return to_ret

def regen_database():
    os.remove(server_dir + "/users.db")
    db = sql.connect(server_dir + "/users.db", check_same_thread=False)
    cr_cursor = db.cursor()
    print(f"{GREEN + Colors.BOLD}>>> {RESET}Created database")

    cr_cursor.execute(table_query)
    db.commit()
    cr_cursor.close()