import hashlib
import os
from Cryptodome.Hash import SHAKE256

# def check_password(hashed_password, user_password):
#     return hashed_password == hashlib.shake256(user_password.encode()).hexdigest()

# password = input("Enter your password: ")

# Password_Byte_Encoded = str.encode(password)
# Hashed_Password = SHAKE256.new()
# Hashed_Password.update(Password_Byte_Encoded)
# pw = Hashed_Password.read(26).hex()

# print(pw)


def password_hashing(password):
    sha256 = hashlib.sha256()
    sha256.update(password)
    password = sha256.hexdigest()
    
    return password

password = input("Enter your password: ")
password = str.encode(password)
print(password_hashing(password))