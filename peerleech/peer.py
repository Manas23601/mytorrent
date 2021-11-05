from ctypes import resize
import bcoding
import hashlib
import random
import requests
import struct
import socket

class Peer():

    def __init__(self, data):

        self.ip = data['ip']
        self.port = data['port']
        self.peer_id = data['peer id']

        self.status = "OK"
    
    def connect_to_peer(self, info_hash, peer_id):
        self.socket = socket.create_connection((self.ip, self.port), 3)
        # requires peer_id which was sent initially to the tracker.
        your_handshake = struct.pack('>B19s8s20s20s', 19, b'BitTorrent protocol', b'\x00'*8, info_hash, peer_id)
        self.socket.sendall(your_handshake)
        peer_handshake = struct.unpack(">B19s8s20s20s" ,self.socket.recv(1 + 19 + 8 + 20 + 20))
        if peer_handshake[4] != self.peer_id:
            print("Error connecting to peer :", self.peer_id)
        print(peer_handshake)
        self.send_message()
    
    def send_message(self):
        interested_message = struct.pack(">IB", 1, 2)
        self.socket.sendall(interested_message)
        unchoke_message = struct.unpack(">IB", self.socket.recv(4 + 1))
        print(unchoke_message)
