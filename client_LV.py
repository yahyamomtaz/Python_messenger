import time
import threading
from socket import *

HEADER_LENGTH = 1000

# ---

s = socket()
shost = gethostname()
ip = gethostbyname(shost)
print(shost, "(", ip, ") \n")
host = input(str("Enter server address:"))
port = 8081
time.sleep(1)
Address = (host, port)
FORMAT = "ASCII"
my_username = input("Username: ")
first_message = (
    "POST / HTTP/1.1\n" "myline: connect\n" "\n" "{}\n" "I want to connect"
).format(my_username)


def connect():
    clientSocket = socket(AF_INET, SOCK_STREAM)
    clientSocket.connect(Address)
    return clientSocket


def send(clientSocket, msg):
    """This function send message to the server"""
    mex = msg.encode()
    clientSocket.send(mex)


def parse_resp(lines):
    code = lines[0].split(" ")[1]
    if code != "200":
        raise Exception(lines[0])
    i = lines.index("")
    headers = lines[:i]
    msgType = headers[-1].split(":")[1].strip(" ")
    messages = lines[i + 1 :]
    return msgType, messages, code, headers


def receiver(my_socket):
    connect = True
    while connect:
        msg = my_socket.recv(1024).decode(FORMAT)
        if not msg:
            continue
        typ, message, _, _ = parse_resp(msg.split("\n"))
        if typ == "message to receive" or typ == "connect":
            print('\n'.join(message))
        time.sleep(1)


def start():

    clientSocket = connect()
    thread_receiver = threading.Thread(target=receiver, args=[clientSocket])
    thread_receiver.start()
    send(clientSocket, first_message)

    header = ("POST / HTTP/1.1\n" "myline: message to send\n" "\n" "{}\n").format(
        my_username
    )
    while clientSocket:
        text = input()
        mex = header + text
        send(clientSocket, mex)


start()
