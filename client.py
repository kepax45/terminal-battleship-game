import socket
import threading

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_ip = "127.0.0.1"
port = 3000

def connect(ip, port):
    server.connect((ip, int(port)))

def create_room():
    server.send('301/'.encode())
    return server.recv(4096).decode()
def join_room(room_code):
    return server.send(('302/'+room_code).encode())

def submit_ships(ships):
    return server.send(('303/'+str(ships)).encode())
def read():
    return server.recv(4096).decode()
def submit_shot(r, c):
    return server.send(('304/' + str([r, c])).encode())