def check_and_split(input_string, substring):
    index = input_string.find(substring)
    if index != -1:
        part_before = input_string[:index + len(substring)]
        part_after = input_string[index + len(substring):]
        return part_before, part_after
    else:
        return None, None

# Beispiel-Nutzung
input_string = '{"message_type": "stbchat_backend", "user_meta": {"username": "Julian"}}{"message_type": "system_message", "message": {"content": "\u001b[36m\u001b[1mWelcome back Julian! Nice to see you!\u001b[39m\u001b[0m"}}'
substring = "}}"

part_before, part_after = check_and_split(input_string, substring)

if part_before is not None:
    print(f"Part before Substring: {part_before}")
    print(f"Part after Substring: {part_after}")
else:
    print(f"Substring '{substring}' not found.")
