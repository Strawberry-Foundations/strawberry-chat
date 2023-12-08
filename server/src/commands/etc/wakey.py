import socket
from .. import register_command
from src.colors import *

@register_command("wakey", 0)
def test_command(socket: socket.socket, username: str, args: list, send):
    send(f"{Colors.ITALIC + YELLOW}Wakey, wakey ...{Colors.RESET}\a")
