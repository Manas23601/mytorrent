from ctypes import resize
import bcoding
import hashlib
import random
from bitstring import BitArray
import requests
import struct
import socket


class Peer():

    def __init__(self, index, ip, port, peer_id):
        self.index = index
        self.peer_id = peer_id
        self.dummy = hashlib.sha1(bytes(random.getrandbits(20))).digest()

        if self.peer_id:
            self.ip = ip
            self.port = port
        else:
            self.ip = ".".join([str(i) for i in ip])
            self.port = int(port[-2]) * 256 +  int(port[-1])

        if not isinstance(self.peer_id, bytes) and self.peer_id:
            self.peer_id =  bytes(str(self.peer_id), encoding = "utf-8")

        # since no peer_id is present uptil now, lets give it some dummy one until we get one from handshake
        if self.peer_id is None:    
            self.peer_id = self.dummy
        # self.status = "OK"
    
    def connect_to_peer(self, info_hash, peer_id):
        # For proxy values
        # https://www.socks-proxy.net/
        # self.socket = socket.create_connection((self.ip, self.port), proxy_type='socks4', proxy_addr='103.168.198.209' , proxy_port='5678', timeout=3)
        print(self.ip, self.port, self.peer_id)
        self.socket = socket.create_connection((self.ip, self.port), 10)
        
        # requires peer_id which was sent initially to the tracker.
        your_handshake = struct.pack('>B19s8s20s20s', 19, b'BitTorrent protocol', b'\x00'*8, info_hash, peer_id)
        self.socket.sendall(your_handshake)
        peer_handshake = struct.unpack('>B19s8s20s20s' ,self.socket.recv(1 + 19 + 8 + 20 + 20))

        if self.peer_id == self.dummy:
            self.peer_id = peer_handshake[4]
        
        if self.peer_id and peer_handshake[4] != self.peer_id:
            print("Error connecting to peer :", self.peer_id, peer_handshake[4])
            return False

        return True
    
    def recieve_message(self, pieces):
        print("Number of pieces:", len(pieces))
        num = '0b' + '0' * len(pieces)
        self.bitmap = BitArray(num)
        self.my_piecess = BitArray(num)

        # get bitfield and have messages
        while True:
            try:
                message = struct.unpack(">IB", self.socket.recv(5))
                length = message[0]
                id = message[1]
                self.all_messages(length, id)
            except Exception as err:
                print(err)
                break
        # send interested message and get unchoke message
        while True:
            print("\nEnter Your Decision:")
            print("\nSend Interested and get choke\nSend request\nRecieve Message\nQuit\nRequest 64 blocks\n")
            decision = int(input())
            if decision == 1:
                message = self.send_interested_message()
                length = message[0]
                id = message[1]
                self.all_messages(length, id)
            if decision == 2:
                print("which piece do u want to request:")
                piece_index = int(input())
                self.request_piece(pieces[piece_index])
            if decision == 3:
                try:
                    message = struct.unpack(">IB", self.socket.recv(5))
                    length = message[0]
                    id = message[1]
                    self.all_messages(length, id)
                except Exception as err:
                    print(err)
            if decision == 4:
                return
            if decision == 5:
                for i in range(64):
                    self.request_piece(pieces[i])
                data = b''
                for i in range(64):
                    data += pieces[i].net_data
                f = open("sample.txt", "wb")
                f.write(data)
                f.close()

    def all_messages(self, length, id):
        if id == 0:
            # choke
            print("You have been choked")
        if id == 1:
            # unchoke
            print("You have been Unchoked")
        if id == 2:
            # interested
            pass
        if id == 3:
            # not interested
            pass
        if id == 4:
            # have
            print("Recieved a Have message")
            index = self.recv_have()
            self.bitmap[index] = 1
        if id == 5:
            # bitfield
            print("Recieved a Bitfield message")
            bits = self.recv_bitfield(length - 1)
            for i in range(len(bits)):
                self.bitmap[i:i+8] = bits[i]
        if id == 6:
            # request
            pass
        if id == 7:
            # piece
            print("You have got a block")
        if id == 8:
            # cancel
            pass

    def recv_have(self):
        have_message = struct.unpack(">I", self.socket.recv(4))
        return have_message[0]

    def recv_bitfield(self, n_bits):
        return [struct.unpack(">B" , self.socket.recv(1)) for i in range(n_bits)]

    def send_interested_message(self):
        interested_message = struct.pack(">IB", 1, 2)
        self.socket.sendall(interested_message)
        unchoke_message = struct.unpack(">IB", self.socket.recv(5))
        return unchoke_message
         
    
    def request_piece(self, piece):
        # request mesage
        for block in piece.blocks:
            request_piece = struct.pack(">IBIII", 13, 6, piece.index, block[0], block[1] - block[0])
            self.socket.sendall(request_piece)
            # piece message
            try:
                block_info = struct.unpack(">IBII", self.socket.recv(4 + 1 + 4 + 4))
                self.all_messages(block_info[0], block_info[1])
            except Exception as Err:
                print("Error Requesting Block")
                return
            block_len = block_info[0] - 9
            for i in range(block_len):
                block[2] += self.socket.recv(1)

        self.verify_hash(piece)

    def verify_hash(self, piece):
        piece.net_data = b''
        for block in piece.blocks:
            piece.net_data += block[2]
        my_hash = hashlib.sha1(piece.net_data).digest()
        if my_hash == piece.hash:
            print(f"Piece {piece.index} Verified")
            piece.verified = True
        else:
            print("Malicious Piece")
