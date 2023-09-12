import scapi
from scapi import Scapi

import yaml
from bardapi import Bard
from yaml import SafeLoader
import threading

with open("bard.yml", encoding="utf-8") as config:
    conf = yaml.load(config, Loader=SafeLoader)

username        = conf["bot"]["username"]
token           = conf["bot"]["token"]
host            = conf["server"]["host"]
port            = conf["server"]["port"]
prefix          = conf["bot"]["prefix"]
bard_token      = conf["bard"]["token"]

Bot = Scapi.Bot(username=username, token=token, host=host, port=port)
Bot.login()
Bot.flag_handler(print_recv_msg=True, enable_user_input=True)

# bard = Bard(token=bard_token)
print(f"{Bot.log_msg}{scapi.BLUE}Successfully connected to the Bard API.{scapi.RESET}")


def Commands():
    while True:
        try:
            message = Bot.recv_message(raw=False, ansi=False)
            
            index       = message.find(":")
            raw_message = message[index + 2:]
            
            if raw_message.startswith(".test"):
                allowed_users   = conf["bard"]["allowed_users"]
                username    = Bot.get_username_by_msg(message)
                print(username)
                
                if username in allowed_users:
                    Bot.send_message("Youre allowed!")
                    
                else:
                    Bot.send_message(f"Youre not allowed.. you are {username} and allowed are {allowed_users}")
                
            elif raw_message.startswith(".bard "):
                allowed_users   = conf["bard"]["allowed_users"]
                username    = Bot.get_username_by_msg(message)            
                
                if username in allowed_users:
                    arg = raw_message.replace("!bard ", "")
                    Bot.send_message("Generating your response... this can take a while...")
                    # response = bard.get_answer(arg)['content']
                    response = "test"
                    
                    Bot.send_message(response)
                    
                else:
                    Bot.send_message(f"{scapi.RED}Sorry, you do not have permissons to do that.{scapi.RESET}")#
                    
            elif raw_message.startswith(".help"):
                help_msg    = f"""
        {scapi.GREEN + scapi.BOLD + scapi.UNDERLINE}* -- Bard Chat Bot -- *{scapi.RESET}
        {scapi.PURPLE}.help:           {scapi.RESET}Help Command
        {scapi.PURPLE}.bard <message>: {scapi.RESET}Chat with bard (Will not always work because of the Bard Token!)
        {scapi.PURPLE}.test:           {scapi.RESET}Just some permission test command{scapi.RESET}"""
                Bot.send_message(help_msg)
                
                
        except Exception as Error: 
            Bot.logger(f"{scapi.RED}An unknown exception occured{scapi.RESET}", type=Bot.type.error)
            Bot.logger(f"{scapi.RED}{Error}{scapi.RESET}", type=Bot.type.error)
            break


@Bot.event
def on_ready():
    print(f"{Bot.log_msg}{scapi.BLUE}Bard Chat Bot started successfully!{scapi.RESET}")
    
BotThread = threading.Thread(target=Bot.run, args=(on_ready,))
CommandThread = threading.Thread(target=Commands)

BotThread.start()
CommandThread.start()