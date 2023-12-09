import socket
from enum import Enum

from src.colors import *
from init import User, ClientSender

class PermissionLevel(Enum):
    MEMBER  = 0
    ADMIN   = 1
    BOT     = 2
    NONE    = -1


command_registry = {}


def register_command(name, arg_count=0, required_permissions=PermissionLevel.MEMBER):
    def decorator(func):
        command_registry[name] = (func, arg_count, required_permissions)
        return func

    return decorator


def execute_command(command_str: str, socket: socket.socket, user_object: User, user_perms: PermissionLevel, args: list, client_sender: ClientSender):
    command_name = command_str
    if command_name in command_registry:
        cmd = command_registry[command_name]
        
        if user_perms.value < cmd[2].value:
            client_sender(f"{RED}Sorry, you do not have permission for this command.{RESET}")
            return
        
        if cmd[1] > args.__len__():
            if cmd[1] == 1:
                argumentsString = "argument"
            else: 
                argumentsString = "arguments"
                
            client_sender(f"{RED}Not enough arguments! The command requires {cmd[1]} {argumentsString} but {args.__len__()} were given.{RESET}")
            return
        
        cmd[0](socket, user_object, args, client_sender)
        
    else:
        client_sender(f"{RED}Command '{command_name}' not found.{RESET}")


def list_commands():
    print(command_registry)
