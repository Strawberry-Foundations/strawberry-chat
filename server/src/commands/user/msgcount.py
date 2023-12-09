from .. import register_command

import socket

from src.colors import *
from src.db import Database

from init import User, ClientSender, server_dir

@register_command("msgcount")
def msgcount_command(socket: socket.socket, user: User, args: list, sender: ClientSender):
    cmd_db = Database(server_dir + "/users.db", check_same_thread=False)
    cmd_db.execute("SELECT msg_count FROM users WHERE username = ?", (user.username,))
    msg_count = cmd_db.fetchone()
    sender.send(f"{GREEN + Colors.BOLD}Your message count:{RESET + Colors.RESET} {msg_count[0]}")
    cmd_db.cursor_close()