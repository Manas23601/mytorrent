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
        message = struct.pack('>B19s8s20s20s', 19, b'BitTorrent protocol', b'\x00'*8, info_hash, peer_id)
        self.socket.sendall(message)
        result = struct.unpack(">B19s8s20s20s" ,self.socket.recv(1 + 19 + 8 + 20 + 20))
        if result[4] != self.peer_id:
            print("Error connecting to peer :", self.peer_id)
        print(result)
