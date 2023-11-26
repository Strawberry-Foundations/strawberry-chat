from .. import register_command, PermissionLevel

import socket

from src.colors import *
from src.functions import doesUserExist
from src.db import Database

from init import server_dir, log, queue

@register_command("queue", arg_count=1, required_permissions=PermissionLevel.ADMIN)
def queue_command(socket: socket.socket, username: str, args: list, send):
    cmd_db = Database(server_dir + "/users.db", check_same_thread=False)

    uname = args[0]
    
    match args[0]:
        case "remove":
            if len(args) == 1:
                if not len(queue.queue) >= 2:
                    send(f"{RED}Cannot remove first position in queue: Only one or none person is currently in queue")
                    return
                
                
                log.info(f"{queue.queue[(position - 1)]} got kicked out of the queue")
                queue.remove()
                send(f"{GREEN}The first position in the queue has been removed")
                
            
            else: 
                position = int(args[1])
                
                try:
                    log.info(f"{queue.queue[(position - 1)]} got kicked out of the queue")
                    queue.remove(pos=(position - 1))
                    send(f"{GREEN}Removed position {position} from the queue")
                except: 
                    send(f"{RED}This position is not available")
                    return
                
                
        
        case "list" | "show":
            queue_list = ""
            
            if len(queue.queue) == 0:
                send(f"{RED}Queue is empty")
                return
                
            for pos, user in enumerate(queue.queue, start=1):
                queue_list = queue_list + f"\n#{pos}: {user}"
                
            send(f"{queue_list}")