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
Bot.flag_handler(print_recv_msg=True, enable_user_input=True, ignore_capitalization=True)

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

@Bot.command(name="dm", arg_count=1)
def send_dm_command(username: str, args: list):
    Bot.send_direct_message(username, " ".join(args))

@Bot.command(name="exit", required_permissions=Scapi.Bot.PermissionLevel.OWNER)
def exit_command(username: str, args: list):
    Bot.exit()

@Bot.event
def on_ready():
    Bot.logger(f"{scapi.BLUE}{Bot.username} started successfully!{scapi.RESET}", type=Scapi.LogLevel.INFO)
    
Bot.run(on_ready)