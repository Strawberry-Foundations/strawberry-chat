from .. import register_command

import socket
import time

from src.vars import default_help_section, user_help_section, admin_help_section, stbchatplus_help_section
from init import User, ClientSender

@register_command("help")
def help_command(socket: socket.socket, user: User, args: list, sender: ClientSender):
    sender.send(default_help_section)
                    
    time.sleep(0.1)
    sender.send(user_help_section)
    
    time.sleep(0.1)
    sender.send(admin_help_section)
    
    time.sleep(0.1)
    sender.send(stbchatplus_help_section)