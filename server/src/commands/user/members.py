from .. import register_command

import socket

from src.colors import *
from src.db import Database

from init import server_dir

@register_command("members")
@register_command("users")
def members_command(socket: socket.socket, username: str, args: list, send):
    cmd_db = Database(server_dir + "/users.db", check_same_thread=False)
    cmd_db.execute("SELECT username FROM users")
    raw_members = cmd_db.fetchall()
    membersLen = len([raw_members for raw_members in sorted(raw_members)])
    members = ", ".join([result[0] for result in raw_members])

    socket.send(f"""{CYAN +  Colors.UNDERLINE + Colors.BOLD}Members on this server ({membersLen}){RESET + Colors.RESET}
        {Colors.BOLD}->{Colors.RESET} {CYAN}{members}{RESET}""".encode("utf8"))