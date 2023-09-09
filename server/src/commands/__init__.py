import socket
from enum import Enum

from src.colors import *

class PermissionLevel(Enum):
    MEMBER = 0
    ADMIN = 1


command_registry = {}


def register_command(name, arg_count=0, required_permissions=PermissionLevel.MEMBER):
    def decorator(func):
        command_registry[name] = (func, arg_count, required_permissions)
        return func

    return decorator


def execute_command(command_str, socket: socket.socket, user: str, user_perms: PermissionLevel, args: list):
    command_name = command_str
    if command_name in command_registry:
        cmd = command_registry[command_name]
        
        if user_perms.value < cmd[2].value:
            socket.send(f"{RED}You lack the permission to use this command!{RESET}".encode("utf8"))
            return
        
        if cmd[1] > args.__len__():
            socket.send(f"Not enough arguments - command requires {cmd[1]} arguments but {args.__len__()} were given".encode("utf8"))
            return
        
        cmd[0](socket, user, args)
        
    else:
        socket.send(f"Command '{command_name}' not found.".encode("utf8"))


def list_commands():
    print(command_registry)
