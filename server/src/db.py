import sqlite3 as sql
import os 
import sys
from init import * 


class Database:
    def __init__(self, database, check_same_thread: bool = ...):
        self.db_connection = sql.connect(database, check_same_thread)
        self.cursor = self.db_connection.cursor()

    def execute(self, statement):
        self.cursor.execute(statement)
    
    def commit(self):
        self.db_connection.commit()
    
    def close(self):
        self.db_connection.close()
        self.cursor.close()