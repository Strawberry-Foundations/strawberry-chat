import yaml
from yaml import SafeLoader
from scapi import Scapi

with open("config.yml", encoding="utf-8") as config:
    conf = yaml.load(config, Loader=SafeLoader)

username    = conf["bot"]["username"]
token       = conf["bot"]["token"]
host        = conf["server"]["host"]
port        = conf["server"]["port"]

Bot = Scapi.Bot(username=username, token=token, host=host, port=port, prefix="!")
Bot.login()
Bot.flagHandler(printReceivedMessagesToTerminal=True, enableUserInput=True)
Bot.run()
