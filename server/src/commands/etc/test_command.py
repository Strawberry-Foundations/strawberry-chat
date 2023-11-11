import socket
from .. import register_command


@register_command("test", 2)
def test_command(socket: socket.socket, username: str, args: list, send):
    send(f"Username: {username}")
    send(f"Args: {args}")
