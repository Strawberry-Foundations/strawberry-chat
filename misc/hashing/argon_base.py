import argon2

def hash_password(password):
    ph = argon2.PasswordHasher()
    hashed_password = ph.hash(password)
    return hashed_password

password = input("Password: ")
print(hash_password(password))