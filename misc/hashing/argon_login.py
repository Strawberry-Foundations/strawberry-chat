import argon2
import sqlite3

def hash_password(password):
    ph = argon2.PasswordHasher()
    hashed_password = ph.hash(password)
    return hashed_password

def register_user(username, password):
    db = sqlite3.connect('users.db')
    c = db.cursor()

    hashed_password = hash_password(password)

    c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))

    db.commit()
    db.close()

def verify_password(stored_password, entered_password):
    ph = argon2.PasswordHasher()
    
    try:
        ph.verify(stored_password, entered_password)
        return True
    
    except argon2.exceptions.VerifyMismatchError:
        return False

def login_user(username, password):
    db = sqlite3.connect('users.db')
    c = db.cursor()
    c.execute("SELECT password FROM users WHERE username = ?", (username,))
    result = c.fetchone()

    if result is not None:
        stored_password = result[0]
        
        if verify_password(stored_password, password):
            print("Login successful")
            
        else:
            print("Wrong password")
            
    else:
        print("User not found")

    db.close()

username = "username"
password = "password"

# register_user(username, password)
login_user(username, password)