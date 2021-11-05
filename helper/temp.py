from ctypes import resize
import bcoding
import hashlib
import random
import requests
import struct
import socket

class Peer():

    def __init__(self):

        self.ip = '148.251.2.71'
        self.port = 50000
        self.peer_id = b'-lt0D80-\x07\xf8\x16\xe3\x96\xb3\xbe8\xd8S\x85\x11'

        self.status = "OK"
    
    def connect_to_peer(self, info_hash, peer_id):
        self.socket = socket.create_connection((self.ip, self.port), 3)
        # requires peer_id which was sent initially to the tracker.
        your_handshake = struct.pack('>B19s8s20s20s', 19, b'BitTorrent protocol', b'\x00'*8, info_hash, peer_id)
        # print(your_handshake)
        self.socket.sendall(your_handshake)
        peer_handshake = struct.unpack('>B19s8s20s20s' ,self.socket.recv(1 + 19 + 8 + 20 + 20))
        if peer_handshake[4] != self.peer_id:
            print("Error connecting to peer :", self.peer_id)
        # print(peer_handshake)
        self.b()
        self.send_message()
    
    def b(self):
        bits = struct.unpack(">IB", self.socket.recv(5))
        bit= []
        for i in range(bits[0] - 1):
            bit.append(struct.unpack(">B", self.socket.recv(1)))
        # print(bits[0], bit)



    def send_message(self):
        interested_message = struct.pack(">IB", 1, 2)
        self.socket.sendall(interested_message)
        unchoke_message = struct.unpack(">IB", self.socket.recv(5))
        # print(unchoke_message)
        self.request_piece()

    def request_piece(self):
        size = 2 ** 14
        piece_length = 262144
        last_block_size = piece_length % size
        num_of_blocks = int((piece_length - last_block_size) / size)
        piece = []
        for i in range(num_of_blocks):
            request_message = struct.pack(">IBIII", 13, 6, 0, i * (2 ** 14) ,size)
            self.socket.sendall(request_message)
            block_1 = struct.unpack(">IBII", self.socket.recv(4 + 1 + 4 + 4))
            print(block_1)
            # print(block_1)
            block = []
            for i in range(block_1[0] - 9):
                block_2 = self.socket.recv(1)
                # block_2 = struct.unpack(">B", self.socket.recv(1))
                block.append(block_2)
            piece.append(block)
        net_item = b''
        for block in piece:
            for num in block:
                net_item += num
        piece_hash = b'\xc0\x99\x8at\xf8\xee\x12vE\x15\xfd7t\xbe4\x04\xa8\xe2E\x00'
        my_hash = hashlib.sha1(net_item).digest()
        print(my_hash)
        if my_hash == piece_hash:
            print("hello")



            
        

peer = Peer()
info_hash = b'\xb2l\x816:\xc1\xa26vS\x85\xa7\x02\xae\xc1\x07\xa4\x95\x81\xb5'
# peer_id = b'\xfa\x83\xda>7\xc7\x90Y\xd7\x8b\x9dq\xb3?Q\xd0\xb22\x84\xec'
peer_id = b'-TR2930-jgk7gju10dw7'
peer.connect_to_peer(info_hash, peer_id)