from .. import register_command

import socket
import time

from src.vars import default_help_section, user_help_section, admin_help_section, stbchatplus_help_section


@register_command("help")
def help_command(socket: socket.socket, username: str, args: list, send):
    send(default_help_section)
                    
    time.sleep(0.1)
    send(user_help_section)
    
    time.sleep(0.1)
    send(admin_help_section)
    
    time.sleep(0.1)
    send(stbchatplus_help_section)