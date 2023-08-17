import yaml
from yaml import SafeLoader
from scapi import Scapi
import threading

with open("config.yml", encoding="utf-8") as config:
    conf = yaml.load(config, Loader=SafeLoader)

username    = conf["bot"]["username"]
token       = conf["bot"]["token"]
host        = conf["server"]["host"]
port        = conf["server"]["port"]

Bot = Scapi.Bot(username=username, token=token, host=host, port=port, prefix="!")
Bot.login()
Bot.flagHandler(printReceivedMessagesToTerminal=True, enableUserInput=True)


def Commands():
    while True:
        message = Bot.recv_message(raw=True)
    
        match message:
            case "Hallo":
                Bot.send_message("Hallo :D")
            
            case "help":
                Bot.send_message("Das kann ich noch nicht. Wie wärs wenn du dir mal die eingebauten Commands anschaust?")

BotThread = threading.Thread(target=Bot.run)
CommandThread = threading.Thread(target=Commands)

BotThread.start()
CommandThread.start()