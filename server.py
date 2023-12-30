import random
import socket
import select
import threading
import time

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_ip = "192.168.1.134"
port = 3000
server.bind((server_ip, port))
server.listen(0)
print(f"Listening on {server_ip}:{port}")
rooms = []


def delete_rooms(socket):
    room = find_room_by_socket(socket)
    if room is not None:
        rooms.remove(room)


def join_room(room_code, socket):
    room = find_room_by_code(room_code)
    if room == None:
        return False
    room['player2'] = socket
    return True
def find_room_by_socket(socket):
    for i in range(len(rooms)):
        if rooms[i]['player1'] is socket or rooms[i]['player2'] is socket:
            return rooms[i]
    return None
def find_room_by_code(room_code):
    for i in range(len(rooms)):
        if rooms[i]['code'] == room_code:
            return rooms[i]
    return None
def get_player_index_by_socket(socket):
    room = find_room_by_socket(socket)
    if room == None:
        return None
    if room['player1'] is socket:
        return 1
    if room['player2'] is socket:
        return 2
    return None
def all_players_connected(room):
    if room['player2'] == None or room['player1'] == None:
        return False
    return True

def all_choices_made(room):
    if room['table1'] != None and room['table2'] != None:
        return True
    return False
def ships_selected(room):
    if room['ships1'] != None and room['ships2'] != None:
        return True
    return False
def collides_ship(point, ships):
    point = (point[0], point[1])
    for ship in ships:
        for coord in ship:
            if point == coord:
                return True
    return False

def generate_room_name():
    return ''.join([chr(random.randint(65, 90)) for i in range(10)])
def handle_client(client_socket, client_adress):
    #print('Started thread')
    game_started = False
    selected_ships = False
    while True:
        data = ''
        try:
            data = client_socket.recv(4096).decode('utf-8')
        except ConnectionResetError as e:
            delete_rooms(client_socket)
            break
        if not data:
            delete_rooms(client_socket)
            client_socket.close()
            break
        if '/' not in data:
            client_socket.send('403'.encode())
            break
        #print(data)
        code, req = data.split('/')
        if code == '301' and len(req) == 0:
            room_code = generate_room_name()
            rooms.append({'code': room_code, 'player1': client_socket, 'player2': None, 'ships1': None, 'ships2': None, 'current_player':random.randint(1, 2), 'guess1':[], 'guess2':[], 'awaiting':False})
            client_socket.send(room_code.encode())
        if code == '302' and len(req) > 0:
            join_room(req, client_socket)
        if code == '303' and len(req) > 0:
            #print('here')
            room = find_room_by_socket(client_socket)
            index = get_player_index_by_socket(client_socket)
            room['ships'+str(index)] = eval(req)
        if code == '304' and len(req) > 0:
            room = find_room_by_socket(client_socket)
            index = get_player_index_by_socket(client_socket)
            new_index = 3 - index
            guess = eval(req)
            if collides_ship(guess, room['ships'+str(new_index)]):
                guess.append('#')
            else:
                guess.append('P')
            room['guess'+str(index)].append(guess)
            room['player'+str(new_index)].send(('203/'+str(room['guess'+str(index)])+'/'+str(room['ships'+str(new_index)])).encode())
            room['player'+str(index)].send(('204/'+guess[-1]).encode())
            room['awaiting'] = True
            time.sleep(1)
            room['awaiting'] = False
            room['current_player'] = new_index
def handle_new_connections():
    while True:
        client_socket, client_address = server.accept()
        print(f"Accepted connection from {client_address[0]}:{client_address[1]}")
        thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
        thread.start()
thread = threading.Thread(target=handle_new_connections, args=())
thread.start()

while True:
    for room in rooms:
        tmp = room
        if tmp == None:
            break
        #print(tmp['guess1'], tmp['guess2'])
        if all_players_connected(tmp) and not ships_selected(tmp):
            tmp['player1'].send('200'.encode())
            tmp['player2'].send('200'.encode())
        if all_players_connected(tmp) and ships_selected(tmp) and tmp['awaiting'] == False:
            index1 = str(tmp['current_player'])
            index2 = str(3 - int(index1))
            tmp['player'+index1].send(('201/'+str(tmp['guess'+index1])).encode())
            tmp['player'+index2].send(('203/'+str(tmp['guess'+index1])+'/'+str(tmp['ships'+index2])).encode())
    time.sleep(0.1)