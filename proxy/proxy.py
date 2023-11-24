# jcom2strProxy - Copyright (c) matteodev8 (info@matteodev.xyz)

import socket
import threading
import time
import sys
import os

import yaml
from yaml import SafeLoader

from helper.strawlog import strawlog

# Load config
with open("config.yml", "r") as cfg_file:
    cfg = yaml.load(cfg_file, Loader=SafeLoader)
    
dbg = cfg['debug']

if dbg:
    strawlog("Debug mode enabled", "DEBUG")
    strawlog("Config loaded: ", "DEBUG")
    strawlog(cfg, "DEBUG")

def start(server_ip, server_port):
    global threadflag
    clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    

    strawlog("Starting jcom2strProxy...", "INFO")
    strawlog(f"Running on Python {sys.version}", "INFO")
    
    try:
        strawlog(f"Trying to connect to {server_ip}:{server_port}...", "INFO")
        clientsocket.connect((server_ip, server_port))
        strawlog("Connected to server!", "INFO")
    except socket.error:
        strawlog("Failed to connect to server!", "ERROR")
        strawlog("Exiting...", "INFO")
        sys.exit(1)
        
    # sendthread = threading.Thread(target=send, args=(clientsocket,))
    # recvthread = threading.Thread(target=recieve, args=(clientsocket,))
    
    # sendthread.start()
    # recvthread.start()
    

    
        
    
start(cfg['server_ip'], cfg['server_port'])
    
