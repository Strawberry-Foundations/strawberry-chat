#!/usr/bin/env python3
import sys
import os

def replace_keywords_in_folder(folder_path, replacements):
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if os.path.isfile(file_path):
            replace_keywords(file_path, replacements)

def replace_keywords(file_path, replacements):
    try:
        with open(file_path, 'r') as file:
            content = file.read()

        for keyword, replacement in replacements.items():
            content = content.replace(keyword, replacement)

        with open(file_path, 'w') as file:
            file.write(content)

        print("Success.")
    except Exception as e:
        print(f"Error while replacing: {e}")


if __name__ == "__main__":
    input_filename = sys.argv[1]
    folder_path = sys.argv[1]
    
    keyword_replacements = {
        'socket.send': 'send',
        '.encode("utf8")': '',
    }

    replace_keywords_in_folder(folder_path, keyword_replacements)
    # replace_keywords(input_filename, keyword_replacements)
