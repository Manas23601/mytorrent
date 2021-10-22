import bcoding
import hashlib
import random
import requests
import struct
import socket

from .piece import Piece
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
        self.name = self.data["info"]["name"]
        # url of tracker
        self.announce_url = self.data["announce"]
        # each packet inside file length
        self.piece_length = self.data["data"]["piece length"]
        # total file length
        self.file_length = self.data["info"]["length"]
        # hash value of all the pieces
        # self.data['info']['pieces']

        # each hash value is of 20 bytes
        pieces = [self.data['info']['pieces'][i:i+20] for i in range(0, len(self.data['info']['pieces']), 20)]
        # make each piece a Piece Class object. Each Object can be downloaded in varying amount of blocks
        self.pieces = [Piece(i, self.piece_length, piece) for i, piece in enumerate(pieces)]
    
    def get_peers(self):
        peer_id = hashlib.sha1(bytes(random.getrandbits(20))).digest()
        
        url = self.data["announce"]
        port = 6882
        # pieces = [self.data['info']['pieces'][i:i+20] for i in range(0, len(self.data['info']['pieces']), 20)]
        downloaded = len(pieces) * self.data["info"]['piece length']

        response = requests.get(url, params={
            'info_hash': self.info_hash,
            'peer_id': peer_id,
            'uploaded': 0,
            'downloaded': downloaded,
            'left': 0,
            'port': port,
            'event': 'started',
        })
        data = bcoding.bdecode(response.content)
        # print(data)
        ip = data["peers"][0]["ip"]
        peer = data["peers"][0]["peer id"]
        port = data["peers"][0]["port"]
        self.socket = socket.create_connection((ip, port), 3)
        print(peer)
        message = struct.pack('>B19s8s20s20s', 19, b'BitTorrent protocol', b'\x00'*8, self.info_hash, peer_id)
        self.socket.sendall(message)
        result = struct.unpack(">B19s8s20s20s" ,self.socket.recv(1 + 19 + 8 + 20 + 20))
        print(result)
        # return bcoding.bdecode(response.content)
