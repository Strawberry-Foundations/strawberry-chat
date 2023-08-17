import scapi
from scapi import Scapi

import yaml
from yaml import SafeLoader
import threading

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
        message = Bot.recv_message(raw=True)
    
        match message:
            case "Hallo":
                Bot.send_message("Hallo :D")
            
            case "!help":
                Bot.send_message("Das kann ich noch nicht. Wie wärs wenn du dir mal die eingebauten Commands anschaust? Nutze dafür /help")
            
            case "!about":
                Bot.send_message(f"{Bot.username} Bot BETA VERSION! Not finished yet")


@Bot.event
def on_ready():
    print(f"{Bot.log_msg}{scapi.BLUE}{Bot.username} started successfully!{scapi.RESET}")
    
BotThread = threading.Thread(target=Bot.run, args=(on_ready,))
CommandThread = threading.Thread(target=Commands)

BotThread.start()
CommandThread.start()