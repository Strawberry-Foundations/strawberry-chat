import scapi
from scapi import Scapi

import yaml
from bardapi import Bard
from yaml import SafeLoader
import threading

with open("bard.yml", encoding="utf-8") as config:
    conf = yaml.load(config, Loader=SafeLoader)

username    = conf["bot"]["username"]
token       = conf["bot"]["token"]
host        = conf["server"]["host"]
port        = conf["server"]["port"]
prefix      = conf["bot"]["prefix"]
token       = conf["bard"]["token"]

bard = Bard(token=token)

Bot = Scapi.Bot(username=username, token=token, host=host, port=port)
Bot.login()
Bot.flagHandler(printReceivedMessagesToTerminal=True, enableUserInput=True)


def Commands():
    while True:
        try:
            message = Bot.recv_message(raw=True)
            
            if message.startswith("!test"):
                Bot.send_message("This is a test message")
            
            elif message.startswith("!bard "):
                arg = message.replace("!bard ", "")
                response = bard.get_answer(arg)['content']
                
                Bot.send_message(response)
                
        except Exception as Error: 
            Bot.logger(f"{scapi.RED}An unknown exception occured{scapi.RESET}", type=Bot.type.error)
            Bot.logger(f"{scapi.RED}{Error}{scapi.RESET}", type=Bot.type.error)
            break


@Bot.event
def on_ready():
    print(f"{Bot.log_msg}{scapi.BLUE}{Bot.username} started successfully!{scapi.RESET}")
    
BotThread = threading.Thread(target=Bot.run, args=(on_ready,))
CommandThread = threading.Thread(target=Commands)

BotThread.start()
CommandThread.start()