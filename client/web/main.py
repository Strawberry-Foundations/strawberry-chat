from flask import Flask, render_template, Response
import datetime
import socket
import threading
import re
import time

app = Flask(__name__)

def currentTime():
    now = datetime.datetime.now()
    formattedTime = now.strftime("%H:%M")
    return formattedTime


@app.route('/')
def index():
    return render_template('index.html')

def escape_ansi(line):
    ansi_escape = re.compile(r'(?:\x1B[@-_]|[\x80-\x9F])[0-?]*[ -/]*[@-~]')
    return ansi_escape.sub('', line)

def recv():
    count = 0
    while threadFlag:
        try:
            message = clientSocket.recv(2048).decode()
                
            if message:
                yield escape_ansi(f"data: [{currentTime()}] {message}\n\n")
                print(escape_ansi(f"data: [{currentTime()}] {message}"))
                
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
    
    app.run()
    
threadFlag = True

if __name__ == '__main__':
    main()
