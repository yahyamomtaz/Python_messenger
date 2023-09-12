import time, socket, sys
import threading


HOST = "0.0.0.0"
s = socket.socket ()
host = socket.gethostname ()
ip = socket.gethostbyname (host)
port = 8081
s.bind ((HOST, port))
print(ip)
FORMAT = "ASCII"
first_message="POST / HTTP/1.1\n"
clients = set()                    #to keep track of all the clients connected
clients_lock = threading.Lock()

def parse_req(lines):    
    method = lines[0].split('/')[0].strip(' ').upper()    
    if method != 'POST':
        raise Exception('HTTP/1.1 405 Method Not Allowed!')    
    i = lines.index('')
    headers = lines[:i]
    msgType = headers[-1].split(':')[1].strip(' ')
    messages = lines[i+1:]
    return msgType, messages, method, headers

def handle_client(clientSocket, clientAddress):
    
    try:
        connected = True
        name = ""
        while connected: 
            try:
                msg = clientSocket.recv(1024).decode(FORMAT)
                if not msg: 
                    continue
                typ, msg,_,_ = parse_req(msg.split('\n'))
                if typ == 'connect':
                    name = msg[0]
                    clientSocket.send("HTTP/1.1 200 OK\n"
                            "myline: connect"
                            "\n"
                            "\n"
                            "HELLO {} NICE TO MEET YOU".format(msg[0]).encode(FORMAT))
                    print("{} connected to the room.".format(msg[0]))
                    continue
                elif typ == 'message to send':
                    clientSocket.send("HTTP/1.1 200 OK\n"
                            "myline: message to send"
                            "\n"
                            "\n"
                            "MESSAGE ACCEPTED FOR DELIVERY".encode(FORMAT))
                    print('From: '+'\n'.join(msg))
                    with clients_lock:
                        notbroken = set()                    
                        for c in clients:
                            try:
                                if c != clientSocket:
                                    header = ("HTTP/1.1 200 OK\n"
                                             "myline: message to receive\n"                                     
                                             "\n"
                                             "From ")
                                    message = header + ('\n'.join(msg))
                                    c.sendall(message.encode(FORMAT))
                                notbroken.add(c)
                            except socket.BrokenPipeError:
                                clients.remove(c)
                    continue
                elif typ == 'message to receive':
                    print('\n'.join(msg))
                    continue
                else:
                    break
            except socket.ConnectionResetError:
                clients.remove(clientSocket)
                print("{} left the room.".format(name))
    finally:
        with clients_lock:
            clients.remove(clientSocket)
        clientSocket.close()
            
            
            
            
            
def start():
    s.listen(1)
    print ('The server is ready to receive')
    while True:                                     # it infinitely waits and try to accept incoming requests
        clientSocket, addr = s.accept()  
        with clients_lock:
            clients.add(clientSocket)      #this unsure us that clients is modified by a single thread each time, to have consistency
            """It deny other thread to modify that client"""
        thread = threading.Thread(target= handle_client , args = (clientSocket, addr)) 
        thread.start()
        """ Each time we have a connection we create a thread, which allows to not block clients while they are not 
        sending messages. 
        We want that while the server waits for others connection , other clients are also able to send messages. """
    





start()
