import pickle
import socket

from copy import deepcopy
from game.utils import get_config
from _thread import start_new_thread

config = get_config()

HOST = config['HOST']
PORT = config['PORT']
BUFFER_SIZE = config['BUFFER_SIZE']
CONNECTIONS = 2

attributes = {
    'x': 0,
    'y': 0,
    'L': False,
    'R': False,
    'U': False,
    'D': True,
    'standing': True,
    'walk count': 0,
    'hit slow': False,
    'bike': False,
    'id': 1,
    'username': 'Noob',
}
players = [deepcopy(attributes), deepcopy(attributes)]  # * CONNECTIONS


def client(conn, player_id: int) -> None:
    with conn:
        conn.send(pickle.dumps(player_id))

        while True:
            try:
                # received player attributes.
                player_attributes = pickle.loads(conn.recv(BUFFER_SIZE))

                players[player_id] = player_attributes

                if not player_attributes:
                    print('Disconnected from server.')
                    break
                else:
                    if player_id == 0:
                        reply = players[1]
                    elif player_id == 1:
                        reply = players[0]
                    else:
                        raise Exception(f'UNEXPECTED PLAYER ID: {player_id}')

                print(reply, player_id)
                conn.sendall(pickle.dumps(reply))
            except socket.error as e:
                print(e)
                break

        current_player = players[player_id]['username']
        print(f'Connection dropped ({current_player}, ID: {player_id}).')


player_id = 0

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:

    s.bind((HOST, PORT))
    s.listen(CONNECTIONS)
    print('Server started, waiting for connection...')

    while True:
        conn, addr = s.accept()
        print('Connected by:', addr, f'Player id: {player_id}')

        start_new_thread(client, (conn, player_id))
        player_id += 1