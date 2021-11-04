from ctypes import resize
import bcoding
import hashlib
import random
import requests
import struct
import socket

class Peer():

    def __init__(self, index, data):

        self.index = index
        self.ip = data['ip']
        self.port = data['port']
        self.peer_id = data['peer id']
        self.status = "OK"
    
    def connect_to_peer(self, info_hash, peer_id):
        self.socket = socket.create_connection((self.ip, self.port), 3)
        
        # requires peer_id which was sent initially to the tracker.
        your_handshake = struct.pack('>B19s8s20s20s', 19, b'BitTorrent protocol', b'\x00'*8, info_hash, peer_id)
        self.socket.sendall(your_handshake)
        peer_handshake = struct.unpack('>B19s8s20s20s' ,self.socket.recv(1 + 19 + 8 + 20 + 20))

        if peer_handshake[4] != self.peer_id:
            print("Error connecting to peer :", self.peer_id)
        
        self.recv_bitfield()
        self.send_message()
    
    def recv_bitfield(self):
        bitfield = struct.unpack(">IB", self.socket.recv(5))
        n_bits = bitfield[0] - 1
        self.bits = [struct.unpack(">B", self.socket.recv(1)) for i in range(n_bits)]
    
    def send_message(self):
        interested_message = struct.pack(">IB", 1, 2)
        self.socket.sendall(interested_message)
        unchoke_message = struct.unpack(">IB", self.socket.recv(5))
        print(unchoke_message)
    
    # -------- Still need to resolve the error in this function --------
    # def request_piece(self, piece):
    #     size = 2 ** 14
    #     piece_length = 262144
    #     last_block_size = piece_length % size
    #     num_of_blocks = int((piece_length - last_block_size) / size)
    #     print(piece)
    #     piece = []
    #     for i in range(piece.n_blocks):
    #         request_message = struct.pack(">IBIII", 13, 6, 0, i * (2 ** 14) , piece.size)
    #         self.socket.sendall(request_message)
    #         response = struct.unpack(">IBII", self.socket.recv(4 + 1 + 4 + 4))
    #         print(response)
    #         block = []
    #         for i in range(response[0] - 9):
    #             bit = self.socket.recv(1)
    #             block.append(bit)
    #         piece.append(block)
        
    #     net_item = b''
    #     for block in piece:
    #         for num in block:
    #             net_item += num
        
    #     piece_hash = b'\xc0\x99\x8at\xf8\xee\x12vE\x15\xfd7t\xbe4\x04\xa8\xe2E\x00'
    #     my_hash = hashlib.sha1(net_item).digest()
    #     print(my_hash)
    #     if my_hash == piece.hash:
    #         print("hello")
