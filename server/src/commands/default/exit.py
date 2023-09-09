import socket
from .. import register_command


@register_command("exit")
@register_command("quit")
def exit_command(stream: socket.socket, username: str, args: list):
    stream.send(f"username: {username}\n".encode("utf8"))
    stream.send(f"args: {args}".encode("utf8"))