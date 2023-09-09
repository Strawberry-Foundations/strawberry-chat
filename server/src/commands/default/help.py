import socket
import time
from .. import register_command
from src.vars import default_help_section, user_help_section, admin_help_section, stbchatplus_help_section


@register_command("help")
def help_command(client: socket.socket, username: str, args: list):
    client.send(default_help_section.encode("utf8"))
                    
    time.sleep(0.1)
    client.send(user_help_section.encode("utf8"))
    
    time.sleep(0.1)
    client.send(admin_help_section.encode("utf8"))
    
    time.sleep(0.1)
    client.send(stbchatplus_help_section.encode("utf8"))