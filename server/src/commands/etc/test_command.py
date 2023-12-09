import socket
from .. import register_command

from init import User, ClientSender


@register_command("test", 2)
def test_command(socket: socket.socket, user: User, args: list, sender: ClientSender):
    sender.send(f"Username: {user.username}")
    sender.send(f"Args: {args}")
