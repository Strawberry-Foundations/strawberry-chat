import hashlib
from Cryptodome.Hash import SHAKE256

def check_password(hashed_password, user_password):
    return hashed_password == hashlib.shake256(user_password.encode()).hexdigest()

password = input("Enter your password: ")

Password_Byte_Encoded = str.encode(password)
Hashed_Password = SHAKE256.new()
Hashed_Password.update(Password_Byte_Encoded)
pw = Hashed_Password.read(26).hex()

print(pw)