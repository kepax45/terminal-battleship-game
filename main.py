import msvcrt
import os
import time

import client
from client import *

def getch_with_timeout(timeout=1):
    start_time = time.time()

    while True:
        if msvcrt.kbhit():
            return msvcrt.getch()

        elapsed_time = time.time() - start_time
        if elapsed_time >= timeout:
            return None  # Timeout reached

def collides_ships(mat, pos):
    for coord in pos:
        row, col = coord
        if mat[row][col] == 'O':
            return True
    return False

def get_cursor_position():
    global r, c, boat_size_horizontal, boat_size_vertical, direction
    if direction == 'h':
        return [(r, c+i) for i in range(boat_size_horizontal)]
    else:
        return [(r+i, c) for i in range(boat_size_vertical)]

def getch():
    return msvcrt.getch()

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def clear_matrix(mat):
    for i in range(len(mat)):
        for j in range(len(mat[0])):
            if mat[i][j] == 'X':
                mat[i][j] = '_'
def place_ship(mat):
    for i in range(len(mat)):
        for j in range(len(mat[0])):
            if mat[i][j] == 'X':
                mat[i][j] = 'O'
    ships.append(get_cursor_position())
def draw_matrix():
    global mat, sent_ships
    print('   A B C D E F G H I J')
    for i in range(len(mat)):
        print((2-len(str(i+1)))*' '+str(i+1) + ' ' + ' '.join(mat[i]))
    if len(keys) == 0 and sent_ships == False:
        print("Press the 'Y' key to confirm your ship placements.")

def remove_ship(mat, pos):
    global ships, keys
    pos = pos[0]
    for i in range(len(ships)):
        if pos in ships[i]:
            for coords in ships[i]:
                row, col = coords
                mat[row][col] = '_'
            keys.append(str(len(ships[i])).encode())
            del ships[i]
            break
            
def clean_matrix(mat):
    for i in range(len(mat)):
        for j in range(len(mat[0])):
            if mat[i][j] == 'X':
                mat[i][j] = '_'
    return mat
def load_cursor():
    global r, c, boat_size_vertical, boat_size_horizontal, mat, direction
    r = max(r, 0)
    r = min(r, n-boat_size_vertical)
    c = max(c, 0)
    c = min(c, n-boat_size_horizontal)
    for coords in get_cursor_position():
        row, col = coords
        if mat[row][col] != 'O':
            mat[row][col] = 'X'
def form_matrix(ships, guesses):
    mat = [['_' for j in range(10)] for i in range(10)]
    for ship in ships:
        for coord in ship:
            row, col = coord
            mat[row][col] = 'O'
    for guess in guesses:
        row, col, sign = guess
        mat[row][col] = sign
    return mat
def time_buffer(last_getch):
    if (time.time_ns()-last_getch)*(10**9) < 0.01:
        time.sleep(0.01)
def guess_matrix(guesses):
    mat = [['_' for i in range(10)] for j in range(10)]
    for guess in guesses:
        row, col, sign = guess
        mat[row][col] = sign
    return mat
def keyboard_handling():
    global boat_size_horizontal, boat_size_vertical, r, c, direction, ch, keys, ships, sent_ships
    if ch == b'd':
        c += 1
        
    if ch == b'a':
        c -= 1
        
    if ch == b's':
        r += 1
        
    if ch == b'w':
        r -= 1

    if ch == b'y' and len(keys) == 0:
        print('Setup confirmed, waiting for the other player...')
        client.submit_ships(ships)
        sent_ships = True

    if ch == b'v' and direction != 'v':
        direction = 'v'
        boat_size_vertical = boat_size_horizontal
        boat_size_horizontal = 1
    if ch == b'c':
        remove_ship(mat, get_cursor_position())
    if ch == b'h' and direction != 'h':
        direction = 'h'
        boat_size_horizontal = boat_size_vertical
        boat_size_vertical = 1
    if ch == b'\r' and not collides_ships(mat, get_cursor_position()) and sent_ships == False:
        place_ship(mat)
        keys.remove(str(max(boat_size_horizontal, boat_size_vertical)).encode())
        boat_size_horizontal = 1
        boat_size_vertical = 1
    if ch == b'\r' and sent_ships == True:
        client.submit_shot(r, c)

    if ch in keys:
        if direction == 'v':
            boat_size_vertical = int(ch.decode('utf-8'))
        else:
            boat_size_horizontal = int(ch.decode('utf-8'))
def game_screen():
    clear_screen()
    global ch
    load_cursor()
    draw_matrix()
    ch = getch_with_timeout(0.5)
    last_getch = time.time_ns()
    keyboard_handling()
    clear_matrix(mat)
    time_buffer(last_getch)

def main_screen():
    connection_menu()
    main_menu()
    return
def connection_menu():
    clear_screen()
    print("Please enter ip and socket port: ", end='')
    ip = input().split(':')
    connect(ip[0], ip[1])
    #connect('127.0.0.1', '3000')
    print('Connected!')
    return
def termination_screen():
    clear_screen()
    print('The game has been terminated.')
    print()
    print('Press any key to go back to the main menu')
    time.sleep(1)
    getch()
    return main_menu()
def update_mode_screen():
    clear_screen()
    draw_matrix()
def main_menu():
    global mat
    clear_screen()
    print('1) Create room')
    print('2) Join room')
    choice = getch()
    if choice == b'1':
        room_code = client.create_room()
        clear_screen()
        print('The code to the room is: ' + room_code)
    elif choice == b'2':
        clear_screen()
        print('Enter room code: ', end='')
        room_code = input()
        response = client.join_room(room_code)
        if response == '404':
            clear_screen()
            print('Incorrect room code, press any key to try again.')
            getch()
            return main_menu()
    while True:
        res = client.read()
        if '/' in res and len(res.split('/')) == 2:
            code, req = res.split('/')
            if code == '201' and len(req) > 0:
                guesses = eval(req)
                mat = guess_matrix(guesses)
                game_screen()
        if '/' in res and len(res.split('/')) == 2:
            code, req = res.split('/')
            if code == '204' and len(req) > 0:
                mat[r][c] = req
                update_mode_screen()
                time.sleep(10)
        if '/' in res and len(res.split('/')) == 3:
            code, guesses, ships = res.split('/')
            if code == '203':
                guesses = eval(guesses)
                ships = eval(ships)
                mat = form_matrix(ships, guesses)
                update_mode_screen()
        if res == '200':
            game_screen()

n = 10

mat = [['_' for i in range(n)] for j in range(n)]
ships = []
r = 0
c = 0
sent_ships = False
boat_size_vertical = 1
boat_size_horizontal = 1
direction = 'h'
keys = [b'2', b'3', b'4', b'5']
clear_screen()

last_getch = time.time_ns()

main_screen()
