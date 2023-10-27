import scapi
from scapi import Scapi

import yaml
from yaml import SafeLoader

with open("default.yml", encoding="utf-8") as config_file:
    config = yaml.load(config_file, Loader=SafeLoader)

username    = config["bot"]["username"]
token       = config["bot"]["token"]
host        = config["server"]["host"]
port        = config["server"]["port"]
prefix      = config["bot"]["prefix"]

Bot = Scapi.Bot(username=username, token=token, host=host, port=port)
Bot.login()
Bot.flag_handler(print_recv_msg=True, enable_user_input=True)

Bot.permission_handler(custom_list=["julian"], owner="julian")

@Bot.command(name="test", arg_count=1, required_permissions=Scapi.Bot.PermissionLevel.CUSTOM)
def test_command(username: str, args: list):
    Bot.send_message(f"""
        Username: {username}
        Args: {args}"""
        )

def Commands():
    while True:
        try:
            recv_message = Bot.recv_message(raw=False, ansi=False)
            index       = recv_message.find(":")
            raw_message = recv_message[index + 2:]
            
            if raw_message.startswith("!"):
                message = raw_message[1:]
                args = message.split()
                cmd = args[0]
                args = args[1:]
                
                Bot.execute_command(cmd, Bot.get_username_by_msg(recv_message), args)
                continue

        except Exception as e: 
            Bot.logger(f"{scapi.RED}An unknown exception occured{scapi.RESET}", type=Scapi.LogLevel.ERROR)
            Bot.logger(f"{scapi.RED}{e}{scapi.RESET}", type=Scapi.LogLevel.ERROR)
            break


@Bot.event
def on_ready():
    print(f"{Bot.log_msg}{scapi.BLUE}{Bot.username} started successfully!{scapi.RESET}")
    
Bot.run(on_ready)