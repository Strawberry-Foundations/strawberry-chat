#!/usr/bin/env python3

import socket
import sys
import colorama
from colorama import Fore
import datetime
import threading
import yaml
from yaml import SafeLoader
import time
import flask
from flask import *

app = Flask(__name__, static_url_path="/static")
app.config["SECRET_KEY"] = "xprivate_ypysKXdjbyMNkBIbx88IFaKlbwiZwn"


# Open Configuration
with open("config.yml") as config:
        data = yaml.load(config, Loader=SafeLoader)
        
lang = data['language']

with open("lang.yml", encoding="utf-8") as langStrings:
        Str = yaml.load(langStrings, Loader=SafeLoader)

# Color Variables
class Colors:
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    RESET = '\033[0m'
    GRAY = "\033[90m"
    
ver = "2.1.2_beta"

def currentTime():
    now = datetime.datetime.now()
    formattedTime = now.strftime("%H:%M")
    return formattedTime


def deleteLastLine():
    cursorUp = "\x1b[1A"
    eraseLine = "\x1b[2K"
    sys.stdout.write(cursorUp)
    sys.stdout.write(eraseLine)


def send(sock):
    while threadFlag:
        try:
            message = input("")
            deleteLastLine()
            sock.send("message".encode("utf8"))

        except:
            print(f"{Fore.RED + Colors.BOLD}{Str[lang]['ErrCouldNotSendMessage']}{Fore.RESET + Colors.RESET}")
            break

def receive(sock):
    while threadFlag:
        try:
            message = sock.recv(2048).decode()
            if message:
                print("[{}] {}".format(currentTime(), message))
            else:
                break
            
        except:
            print(f"{Fore.RED + Colors.BOLD}{Str[lang]['ErrNotReachable']}{Fore.RESET + Colors.RESET}")
            break

def web():
    app.run(host="0.0.0.0", port=80, threaded=True)

def main():
    global threadFlag
    colorama.init()

    socketFamily = socket.AF_INET
    socketType = socket.SOCK_STREAM
    clientSocket = socket.socket(socketFamily, socketType)
    
    # Connects to the server
    try: 
        print(f"{Fore.YELLOW + Colors.BOLD}{Str[lang]['TryConnection']}{Fore.RESET + Colors.RESET}")
        clientSocket.connect(("192.168.0.157", 8080))
    except: 
        print(f"{Fore.RED + Colors.BOLD}{Str[lang]['ErrNotReachable']}{Fore.RESET + Colors.RESET}")
        sys.exit(1)
        
    sendingThread = threading.Thread(target=send, args=(clientSocket,))
    receivingThread = threading.Thread(target=receive, args=(clientSocket,))
    webThread = threading.Thread(target=web)

    receivingThread.start()
    sendingThread.start()
    webThread.start()
    

    try:
        while receivingThread.is_alive() and sendingThread.is_alive():
            continue
        
    except KeyboardInterrupt:
        print(f"\n{Str[lang]['Aborted']}")
        threadFlag = False
        sys.exit(1)
        
    threadFlag = False

    clientSocket.close()
    print(f"\n{Str[lang]['CloseApplication']}")
    


threadFlag = True

if __name__ == "__main__":
    main()
    pass