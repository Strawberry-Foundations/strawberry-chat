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

@Bot.on_message(message="Hello")
def on_hello_message(username: str):
    Bot.send_message(f"Hello {username}!")

@Bot.command(name="test", arg_count=1, required_permissions=Scapi.Bot.PermissionLevel.CUSTOM)
def test_command(username: str, args: list):
    Bot.send_message(f"""
        Username: {username}
        Args: {args}"""
        )

@Bot.event
def on_ready():
    Bot.logger(f"{scapi.BLUE}{Bot.username} started successfully!{scapi.RESET}", type=Scapi.LogLevel.INFO)
    
Bot.run(on_ready)