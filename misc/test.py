import sqlite3 as sql

db = sql.connect('./users.db')
c = db.cursor()

username = "Julian"
password = "Julian"

c.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))

if c.fetchall():
    c.execute('SELECT username FROM users WHERE username = ? AND password = ?', (username, password))
    result = c.fetchone()
    if result is not None:
        # Den Benutzernamen als String extrahieren
        username = result[0]
        print("Benutzername:", username)
