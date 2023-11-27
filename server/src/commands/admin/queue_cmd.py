from .. import register_command, PermissionLevel

import socket

from src.colors import *
from src.functions import doesUserExist
from src.db import Database

from init import server_dir, log, queue, LogMessages

@register_command("queue", arg_count=1, required_permissions=PermissionLevel.ADMIN)
def queue_command(socket: socket.socket, username: str, args: list, send):
    cmd_db = Database(server_dir + "/users.db", check_same_thread=False)

    uname = args[0]
    
    match args[0]:
        case "remove":
            if len(args) == 1:
                try:                
                    log.info(LogMessages.queue_kick % queue.queue[0]) 
                    queue.remove()
                    send(f"{GREEN}The first position in the queue has been removed")
                    
                except: 
                    send(f"{RED}Queue is empty")
                    return
                
            
            else: 
                position = int(args[1])
                
                try:
                    log.info(LogMessages.queue_kick % queue.queue[(position - 1)]) 
                    queue.remove(pos=(position - 1))
                    send(f"{GREEN}Removed position {position} from the queue")
                    
                except: 
                    send(f"{RED}This position is not available")
                    return
                
                
        case "let" | "admit":
            pass
        
        case "list" | "show":
            queue_list = ""
            
            if len(queue.queue) == 0:
                send(f"{RED}Queue is empty")
                return
                
            for pos, user in enumerate(queue.queue, start=1):
                queue_list = queue_list + f"\n#{pos}: {user}"
                
            send(f"{queue_list}")