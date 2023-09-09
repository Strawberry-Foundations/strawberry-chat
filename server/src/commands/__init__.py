from etc.ping_command import *

command_registry = {}


def register_command(name, arg_count=0):
    def decorator(func):
        command_registry[name] = (func, arg_count)
        return func
    return decorator


def execute_command(command_str):
    command_name = command_str
    if command_name in command_registry:
        command_func, arg_count = command_registry[command_name]
    else:
        print(f"Command '{command_name}' not found.")

register_command("test",0)(ping_command.register_command())