import random
import base64

user_id = input("User ID: ")
pw_part_4 = base64.b64encode(user_id.encode('utf-8'))
pw_part_4 = pw_part_4.decode('utf-8').replace("=", "")


def generate_token():
    characters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    pw_part_1 = ""
    pw_part_2 = ""
    pw_part_3 = ""
    for _ in range(12):
        pw_part_1 += random.choice(characters)
        pw_part_2 += random.choice(characters)
        pw_part_3 += random.choice(characters)

    password = pw_part_1 + "_" + pw_part_2 + "." + pw_part_3 + "." + pw_part_4
    return password

def main():
    """Generates and prints the bot token."""
    password = generate_token()
    print(password)

main()