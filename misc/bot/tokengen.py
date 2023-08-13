import random

def generate_token():
    characters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    pw_part_1 = ""
    pw_part_2 = ""
    pw_part_3 = ""
    for _ in range(12):
        pw_part_1 += random.choice(characters)
        pw_part_2 += random.choice(characters)
        pw_part_3 += random.choice(characters)
    
    password = pw_part_1 + "-" + pw_part_2 + "-" + pw_part_3
    return password

def main():
  """Generates and prints the bot token."""
  password = generate_token()
  print(password)

if __name__ == "__main__":
  main()