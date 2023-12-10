from flask import *
import datetime
import socket
import threading
import re
import time

app = Flask(__name__)

# Return current time
def current_time(): return datetime.datetime.now().strftime("%H:%M")

# Escape ansi from a string
def escape_ansi(string: str): return re.compile(r'(?:\x1B[@-_]|[\x80-\x9F])[0-?]*[ -/]*[@-~]').sub('', string)

# Convert raw input to json data
def conv_json_data(data): return json.loads(data)

# Handle user badges
def badge_handler(badge):
    if not badge == "":
        return " [" + badge + "]"
    else:
        return ""

@app.route('/')
def index():
    return "Currently nothing here >->"

@app.route('/chat', methods=['GET', 'POST'])
def chat():
    global uname
    global password
    uname = request.args.get('uname')
    password = request.args.get('password')
    
    if request.method == "POST":
        message = request.form['message']
        clientSocket.send(message.encode("utf8"))
    
    return render_template('chat.html')

def escape_ansi(line):
    ansi_escape = re.compile(r'(?:\x1B[@-_]|[\x80-\x9F])[0-?]*[ -/]*[@-~]')
    return ansi_escape.sub('', line)

def recv():
    clientSocket.send("jules".encode("utf8"))
    time.sleep(0.1)
    clientSocket.send("test".encode("utf8"))
    
    while threadFlag:
        try:
            message = clientSocket.recv(2048).decode()
            
            try:
                message = conv_json_data(message)
            except:
                message = message
            
            if message:
                try:
                    message_type = message["message_type"]
                    
                except Exception as e:
                    message_type = "unknown"    
                    continue
                
                match message_type:
                    case "user_message":
                        username    = message["username"]
                        nickname    = message["nickname"]
                        badge       = badge_handler(message["badge"])
                        role_color  = message["role_color"]
                        message     = message["message"]["content"]
                            
                yield escape_ansi(f"data: [{current_time()}] {message}\n\n")
                print(escape_ansi(f"data: [{current_time()}] {message} --> {username}"))
                
            else:
                break
            
        except Exception as e:
            print(e)
            break
        
def send(sock):
    while threadFlag:
        try:
            message = input("")
            sock.send(message.encode("utf8"))

        except:
            print(f"Could not send the message!")
            break
        
        
@app.route('/updates')
def updates():
    return Response(recv(), content_type='text/event-stream')

def main():
    global threadFlag
    global clientSocket
    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientSocket.connect(("192.168.0.157", 8080))
    
    sendingThread = threading.Thread(target=send, args=(clientSocket,))
    sendingThread.start()
    
    app.run(host="0.0.0.0")
    
threadFlag = True

if __name__ == '__main__':
    main()
