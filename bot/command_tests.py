import scapi
from scapi import Scapi

import socket
import yaml
from yaml import SafeLoader
import threading
import random

with open("default.yml", encoding="utf-8") as config:
    conf = yaml.load(config, Loader=SafeLoader)

username    = conf["bot"]["username"]
token       = conf["bot"]["token"]
host        = conf["server"]["host"]
port        = conf["server"]["port"]
prefix      = conf["bot"]["prefix"]

Bot = Scapi.Bot(username=username, token=token, host=host, port=port)
Bot.login()
Bot.flag_handler(printReceivedMessagesToTerminal=True, enableUserInput=True)

@Bot.command(name="test", arg_count=0, required_permissions=Scapi.Bot.PermissionLevel.CUSTOM, custom_permissions=["julian"])
def test_command(username: str, args: list):
    Bot.send_message(f"Username: {username}")

def Commands():
    while True:
        # try:
            message = Bot.recv_message(raw=True)
            
            if message.startswith("!"):
                message = message[1:]
                args = message.split()
                cmd = args[0]
                args = args[1:]
                
                role = "member"
                match role:
                    case "member":
                        role = Scapi.Bot.PermissionLevel.ALL
                    case "admin":
                        role = Scapi.Bot.PermissionLevel.ADMIN
                        
                Bot.execute_command(cmd, Bot.get_username_by_msg(message), args)
                continue

        # except Exception as e: 
        #     Bot.logger(f"{scapi.RED}An unknown exception occured{scapi.RESET}", type=Scapi.LogLevel.ERROR)
        #     Bot.logger(f"{scapi.RED}{e}{scapi.RESET}", type=Scapi.LogLevel.ERROR)
        #     break


@Bot.event
def on_ready():
    print(f"{Bot.log_msg}{scapi.BLUE}{Bot.username} started successfully!{scapi.RESET}")
    
BotThread = threading.Thread(target=Bot.run, args=(on_ready,))
CommandThread = threading.Thread(target=Commands)

BotThread.start()
CommandThread.start()