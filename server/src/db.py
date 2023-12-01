import sqlite3

class SQLiteDatabaseWrapper:
    def __init__(self, database_path):
        self.database_path = database_path
        self.connection = None

    def connect(self):
        self.connection = sqlite3.connect(self.database_path)
        self.connection.row_factory = sqlite3.Row

    def disconnect(self):
        if self.connection:
            self.connection.close()

    def execute_query(self, query, parameters=None):
        if not self.connection:
            raise RuntimeError("Not connected to the database. Call connect() first.")

        cursor = self.connection.cursor()
        if parameters:
            cursor.execute(query, parameters)
        else:
            cursor.execute(query)

        return cursor

    def fetch_all(self, query, parameters=None):
        cursor = self.execute_query(query, parameters)
        return cursor.fetchall()

    def fetch_one(self, query, parameters=None):
        cursor = self.execute_query(query, parameters)
        return cursor.fetchone()

    def commit(self):
        if self.connection:
            self.connection.commit()

    def rollback(self):
        if self.connection:
            self.connection.rollback()