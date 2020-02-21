#use socket and threading to handle connections
import socket
from _thread import *
import pickle

HOST = "192.168.1.147"
PORT = 5555
buffer_size = 2048

attributes = {
'x':0,
'y':0,
'L':False,
'R':False,
'U':False,
'D':True,
'standing':True,
'walk count':0,
'hit slow': False,
'inventory': [],
'bike': False,
'mushroom': False,
'stats': {
	'kills':0,
	'deaths':0,
	'K/D': 0
	},
'killed': None,
'dead': False,
'ID':None
}
players = [attributes]*3

def client(conn, player):
	with conn:
		conn.send(pickle.dumps(player)) #send player ID
		while True: #continously run whilst client still connected
			try:
				data = pickle.loads(conn.recv(buffer_size)) #received player attrs
				players[player] = data

				if not data:
					print('Disconnected from server.')
					break
				else:
					#slice out this player and return other players only
					reply = (players[:player]+players[player+1:])[0]
					# if player == 1:
					# 	reply = players[0]
					# else:
					# 	reply = players[1]

				conn.sendall(pickle.dumps(reply)) 
			except:
				break

		#player DCed so reset to defaults and add to DC list so we can re-add if they re-connect
		players[player] = attributes
		DC.append(player)
		print(f'connection dropped (player {player}).')

DC = [] #disconnected player IDs
clients = set()
player = 0 #player ID
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s: #IPV4 adress, TCP

	s.bind((HOST, PORT))
	s.listen(10) #listen for up to 10 connections
	print("Server started, waiting for connection...")

	while True: #continuously look for connections, if found, start new thread
		conn, addr = s.accept()
		print("Connected by:", addr)
		if len(DC):
			DC_player = DC.pop()
			start_new_thread(client, (conn, DC_player))
		else:
			start_new_thread(client, (conn, player))
			player += 1