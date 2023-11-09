# Warning: This is unfinished and should not be used anymore

import sys
import socket
import colorama
from colorama import Fore
import datetime
import threading
import requests
import re
import time
import yaml
from yaml import SafeLoader

with open("config.yml", encoding="utf-8") as config_file:
    config = yaml.load(config_file, Loader=SafeLoader)

webhook_url     = config["webhook"]["url"]
stbchat_host    = config["stbchat"]["server"]["host"]
stbchat_port    = config["stbchat"]["server"]["port"]

class Colors:
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    RESET = '\033[0m'


def get_username_by_msg(message):
    username = message.split(":")[0]
    username = username.replace("[", "") \
                    .replace("]", "") \
                    .replace("👑", "") \
                    .replace("😎", "") \
                    .replace("🔥", "") \
                    .replace("🫐", "") \
                    .replace("🤖", "") \
                    .replace("💪", "") \
                    .replace("👍", "") \
                    .replace("🤡", "") \
                    .replace("😈", "") \
                    .replace("🤝", "") \
                    .replace("👋", "") \
                    .replace("😌", "") \
                    .replace("🍓", "") \
                    .replace("💫", "") \
                    .replace("9mm", "") \
                    .replace("1mm", "") \
                                
    username_index  = username.find("(")
    raw_username    = username[username_index + 1:]
    raw_username    = raw_username.replace(")", "").replace("@", "").replace(" ", "")
    
    return raw_username

def currentTime():
    now = datetime.datetime.now()
    formattedTime = now.strftime("%H:%M")
    return formattedTime

def deleteLastLine():
    cursorUp = "\x1b[1A"
    eraseLine = "\x1b[2K"
    sys.stdout.write(cursorUp)
    sys.stdout.write(eraseLine)

def escape_ansi(line):
    ansi_escape = re.compile(r'(?:\x1B[@-_]|[\x80-\x9F])[0-?]*[ -/]*[@-~]')
    return ansi_escape.sub('', line)

def send(sock):
    sock.send("Discord".encode("utf8"))
    time.sleep(1)
    sock.send("6My5Kn8MOE6W_6cU8ow01ynoV.Mv3wuIWoJh48.MDAwMC0wMDA3".encode("utf8"))
    time.sleep(1)
    
    while threadFlag:
        try:
            message = input("")
            deleteLastLine()
            sock.send(message.encode("utf8"))

        except Exception as e:
            print(e)
            break

def receive(sock):
    count = 0
    
    while threadFlag:        
        try:
            message = str
            message = sock.recv(2048).decode()
            
            if message:
                # print("[{}] {}".format(currentTime(), message))
                username = get_username_by_msg(escape_ansi(message))
                
                data = {
                    "content" : f"{escape_ansi(message)}",
                    "username" : f"{username}"
                    }
                
                count = count + 1
                
                if count > 7:
                    if username.lower() == "discord":
                        pass
                    else:
                        requests.post(webhook_url, json = data)
            else:
                break
            
        except Exception as e:
            print(e)
            break

def main():
    global threadFlag
    colorama.init()
    socketFamily = socket.AF_INET
    socketType = socket.SOCK_STREAM
    clientSocket = socket.socket(socketFamily, socketType)
    
    try: 
        clientSocket.connect((stbchat_host, stbchat_port))
    except: 
        print("server not reachable")
        exit(1)
        
    print(f"{Fore.GREEN}connected to server{Fore.RESET}\n")
    sendingThread = threading.Thread(target=send, args=(clientSocket,))
    receivingThread = threading.Thread(target=receive, args=(clientSocket,))
    receivingThread.start()
    sendingThread.start()
    
    try:
        while receivingThread.is_alive() and sendingThread.is_alive():
            continue
    except KeyboardInterrupt:
        print(f"\nAborted")
        threadFlag = False
        exit(1)
    
    threadFlag = False
    clientSocket.close()
    print(f"\nClosed application")

threadFlag = True

if __name__ == "__main__":
    main()
    pass