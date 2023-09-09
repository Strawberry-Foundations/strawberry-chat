import socket
from .. import register_command


@register_command("test", 2)
def test_command(socket: socket.socket, username: str, args: list):
    socket.send(f"Username: {username}".encode("utf8"))
    socket.send(f"Args: {args}".encode("utf8"))
