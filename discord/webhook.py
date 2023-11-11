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
import json

import scapi
from scapi import Scapi

with open("config.yml", encoding="utf-8") as config_file:
    config = yaml.load(config_file, Loader=SafeLoader)

webhook_url     = config["webhook"]["url"]
stbchat_host    = config["stbchat"]["server"]["host"]
stbchat_port    = config["stbchat"]["server"]["port"]

class Colors:
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    RESET = '\033[0m'


def current_time(): return datetime.datetime.now().strftime("%H:%M")
def conv_json_data(data): return json.loads(data)

def delete_last_line():
    sys.stdout.write("\x1b[1A")
    sys.stdout.write("\x1b[2K")

def badge_handler(badge):
    if not badge == "":
        return " [" + badge + "]"
    else:
        return ""

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
            delete_last_line()
            sock.send(message.encode("utf8"))

        except Exception as e:
            print(e)
            break

def receive(sock):
    count = 0
    
    while threadFlag:
        try:
            message = sock.recv(2048).decode('utf-8')

            try: message = conv_json_data(message)
            except: message = message
            
            if message:
                try:
                    try: message_type = message["message_type"]
                    except: message_type = "unknown"
                    
                    if message_type == "user_message":
                        username    = message["username"]
                        nickname    = message["nickname"]
                        badge       = badge_handler(message["badge"])
                        role_color  = message["role_color"]
                        message     = message["message"]["content"]
                        
                        if nickname == username:
                            fmt = f"[{current_time()}] {role_color}{username}{badge}:\033[0m {message}"
                        else:
                            fmt = f"[{current_time()}] {role_color}{nickname} (@{username.lower()}){badge}:\033[0m {message}"
                            
                        print(fmt)
                        
                    else:
                        message     = message["message"]["content"]                    
                    count = count + 1
                    # print(count)
                    
                    if message_type == "user_message" and count > 7 and not username.lower() == "discord":
                        raw_username = username
                        
                        if nickname == username:
                            username = username
                        
                        else:
                            username = f"{nickname} (@{username.lower()})"
                        
                        # timestamp = datetime.datetime.now()
                        timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

                        print(timestamp)
                        
                        data = {
                            "username" : f"{raw_username}",
                            "embeds": [{
                                "title": f"{username} {badge}",
                                "description": f"{message}",
                                "color": 16711680,
                                "timestamp":timestamp,
                                "author": {
                                    "name": "Strawberry Chat Bridge",
                                    "icon_url": "https://media.discordapp.net/attachments/880513737948270642/1173024808187994153/sf_logo_small.png"
                                }
                            }]
                        }     
                        
                        requests.post(webhook_url, json = data)
                    else: pass
                
                except Exception as e:
                    time.sleep(0.05)
                    message         = message["message"]["content"]
                        
            else: break
            
        except Exception as e: 
            pass

                        
                        
                        
                    
                    #     data = {
                    #     "content" : f"{escape_ansi(fmt)}",
                    #     "username" : f"{username}"
                    #     }
                        
                    #     count = count + 1
                
                    #     if count > 7:
                    #         if username.lower() == "discord":
                    #             pass
                    #         else:
                    #             requests.post(webhook_url, json = data)
                        
                    # else:
                    #     message     = message["message"]["content"]    

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
    
    
    log_msg = f"{scapi.CYAN + scapi.BOLD}{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  {scapi.BLUE}INFO   scapi  -->  {scapi.RESET}"
    print(f"{log_msg}{scapi.GREEN}Webhook started - Connected to server{scapi.RESET}")
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