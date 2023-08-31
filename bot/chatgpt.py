import scapi
from scapi import Scapi

import yaml
from yaml import SafeLoader
import threading
import random

with open("config.yml", encoding="utf-8") as config:
    conf = yaml.load(config, Loader=SafeLoader)

username    = conf["bot"]["username"]
token       = conf["bot"]["token"]
host        = conf["server"]["host"]
port        = conf["server"]["port"]
prefix      = conf["bot"]["prefix"]

Bot = Scapi.Bot(username=username, token=token, host=host, port=port)
Bot.login()
Bot.flagHandler(printReceivedMessagesToTerminal=True, enableUserInput=True)


def Commands():
    while True:
        try:
            message = Bot.recv_message(raw=True)
            
            if message.rstrip() == "test":
                print("RECEIVED MESSAGE IS TEST")
                
        except: 
            Bot.logger(f"{scapi.RED}An unknown exception occured{scapi.RESET}", type=Bot.type.error)
            break


@Bot.event
def on_ready():
    print(f"{Bot.log_msg}{scapi.BLUE}{Bot.username} started successfully!{scapi.RESET}")
    
BotThread = threading.Thread(target=Bot.run, args=(on_ready,))
CommandThread = threading.Thread(target=Commands)

BotThread.start()
CommandThread.start()