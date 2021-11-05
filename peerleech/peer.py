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
            return False
        
        self.recv_bitfield()
        self.send_message()
        return True
    
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
    def request_piece(self, piece):
        size = 2 ** 14

        blocks_of_piece = []
        for begin, end, _ in piece.blocks:
            request_piece = struct.pack(">IBIII", 13, 6, piece.index, begin, size)
            self.socket.sendall(request_piece)
            block_info = struct.unpack(">IBII", self.socket.recv(4 + 1 + 4 + 4))

            block_len = block_info[0] - 9
            block = []
            for i in range(block_len):
                block.append(self.socket.recv(1))
            blocks_of_piece.append(block)
        
        net_item = b''
        for block in blocks_of_piece:
            for block_part in block:
                net_item += block_part

        my_hash = hashlib.sha1(net_item).digest()
        if my_hash == piece.hash:
            print("hello")
