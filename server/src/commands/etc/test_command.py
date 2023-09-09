import socket

from .. import register_command


@register_command("test", 2)
def test_command(stream: socket.socket, username: str, args: list):
    stream.send(f"Username: {username}".encode("utf8"))
    stream.send(f"Args: {args}".encode("utf8"))
