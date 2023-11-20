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
    
if cfg['debug']:
    strawlog("Debug mode enabled", "debug")
    

def start(ip, port):
    if cfg['proxy_mode'] == "srv-only":
        strawlog("Starting in server-only mode", "info")
        srv(ip, port)
    
    if cfg['proxy_mode'] == "client-only":
        strawlog("Starting in client-only mode", "info")
        client(ip, port)        

    if cfg['proxy_mode'] == "srv-client":
        strawlog("Starting in dual mode", "info")
        dual(ip, port)
        
        

def srv(ip, port):
    strawlog(f"Trying to connect to {ip}:{port}", "info")

def client(ip, port):
    strawlog(f"Trying to connect to {ip}:{port}", "info")

def dual(ip, port):
    strawlog("Dual mode is experimental! Use at your own risk!", "warning")
    strawlog(f"Trying to connect to {ip}:{port}", "info")
    
start("69.69.69.69", "42088")
    
