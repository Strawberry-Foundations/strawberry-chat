import scapi
from scapi import Scapi

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
Bot.flagHandler(printReceivedMessagesToTerminal=True, enableUserInput=True)


def Commands():
    while True:
        try:
            message = Bot.recv_message(raw=True)
        
            if message.startswith("!rps "):
                choices = ["schere", "stein", "papier"]
                bot_choice = random.choice(choices)
                arg = message.replace("!rps ", "")
                
                if arg == "":
                    Bot.send_message("Du musst schon eine Möglichkeit angeben... Es gibt Schere, Stein oder Papier!")
                    continue
                
                else:
                    if arg.lower() not in choices:
                        Bot.send_message("Du musst schon eine richtige Möglichkeit angeben... Es gibt Schere, Stein oder Papier!")
                        
                    else:
                        def determine_winner(user, computer):
                            if user == computer:
                                return "Unentschieden!"
                            elif user == "schere":
                                return "Du gewinnst!" if computer == "papier" else "Du verlierst!"
                            elif user == "stein":
                                return "Du gewinnst!" if computer == "schere" else "Du verlierst!"
                            elif user == "papier":
                                return "Du gewinnst!" if computer == "stein" else "Du verlierst!"
                        
                        
                        Bot.send_message(f"""
        * -- Schere, Stein, Papier! -- *
        Du hast {arg.capitalize()}...
        Ich habe {bot_choice.capitalize()}!
        {determine_winner(arg.lower(), bot_choice.lower())}""")
                
            match message:
                case "Hallo":
                    Bot.send_message("Hallo :D")
                
                case "!help":
                    help_msg    = f"""
            {scapi.BLUE + scapi.BOLD + scapi.UNDERLINE}* -- Strawberry Bot -- *{scapi.RESET}
            {scapi.CYAN}!help:           {scapi.RESET}Help Command
            {scapi.CYAN}!rps <choice>: {scapi.RESET}Schere, Stein, Papier!
            {scapi.CYAN}!about:           {scapi.RESET}About Strawberry Bot{scapi.RESET}"""
                    Bot.send_message(help_msg)
                
                case "!about":
                    Bot.send_message(f"{Bot.username} Bot BETA VERSION! Not finished yet")
                    
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