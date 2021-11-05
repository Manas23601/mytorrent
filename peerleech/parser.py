import bcoding
import hashlib
import random
import requests
import struct
import socket
import os

from .peer import Peer
class Torrent:
    def __init__(self, file_path):
        # open the .torrent file and decode it (encoded in bencode)
        try:
            with open(file_path, "rb") as f:
                self.data = bcoding.bdecode(f.read())
        except EnvironmentError as err: # parent of IOError, OSError *and* WindowsError where available
            print(err)
        
        self.info = self.data["info"]
        # info dictionary sha-1 hash value
        self.info_hash = hashlib.sha1(bcoding.bencode(self.data["info"])).digest()
        # name of the file
        self.folder_name = self.data["info"]["name"]
        # url of tracker
        self.announce_url = self.data["announce"]
        # each packet inside file length
        self.piece_length = self.data["info"]["piece length"]
    
        self.pieces = [self.data['info']['pieces'][i:i+20] for i in range(0, len(self.data['info']['pieces']), 20)]

        if self.data["info"]["files"]:
            folder = "download"
            if self.data["title"]:
                folder = self.data["title"]
            path = os.path.join(os.getcwd(), folder)
            if not os.path.isdir(path):
                os.mkdir(path)
        
        
    
    #make a get request to the tracker to fetch the peer ips
    def connect_to_tracker(self):
        
        # 20 byte long
        self.peer_id = hashlib.sha1(bytes(random.getrandbits(20))).digest()
        print(self.peer_id)
        port = 6882
        left = self.file_length

        response = requests.get(self.announce_url, params={
            'info_hash': self.info_hash,
            'peer_id': self.peer_id,
            'uploaded': 0,
            'downloaded': 0,
            'left': left,
            'port': port,
            'event': 'started',
        })
        data = bcoding.bdecode(response.content)
        print(data)
        self.add_peers(data)
    
    def add_peers(self, data):
        for peer in data["peers"]:
            self.peer_list.append(Peer(peer))

        self.run_connect()
    
    def run_connect(self):
        self.peer_list[0].connect_to_peer(self.info_hash, self.peer_id)



# ip = data["peers"][0]["ip"]
# peer = data["peers"][0]["peer id"]
# port = data["peers"][0]["port"]
# self.socket = socket.create_connection((ip, port), 3)
# print(peer)
# message = struct.pack('>B19s8s20s20s', 19, b'BitTorrent protocol', b'\x00'*8, self.info_hash, peer_id)
# self.socket.sendall(message)
# result = struct.unpack(">B19s8s20s20s" ,self.socket.recv(1 + 19 + 8 + 20 + 20))
# print(result)
# return bcoding.bdecode(response.content)




# # each hash value is of 20 bytes
# pieces = [self.data['info']['pieces'][i:i+20] for i in range(0, len(self.data['info']['pieces']), 20)]
# # make each piece a Piece Class object. Each Object can be downloaded in varying amount of blocks
# self.pieces = [Piece(i, self.piece_length, piece) for i, piece in enumerate(pieces)]