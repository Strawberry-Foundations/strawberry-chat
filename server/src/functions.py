import socket
import threading

import os
import sys
import logging
import sqlite3 as sql

import yaml
from yaml import SafeLoader

import atexit
import datetime
import time
import errno
import random
import requests
import re

from colorama import Fore, Style

# Receive your global ip address for verification
def get_global_ip():
    response = requests.get('https://api.ipify.org?format=json')
    data = response.json()
    return data['ip']