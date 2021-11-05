import bcoding
import hashlib
import random
import requests
import struct
import socket

from .peer import Peer
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
        self.piece_length = self.data["info"]["piece length"]
        # total file length
        self.file_length = self.data["info"]["length"]

        # add_peers is going to store peer objects in this list
        self.peer_list = []
        self.piece_list = []

    #make a get request to the tracker to fetch the peer ips
    def get_from_tracker(self):
        
        # 20 byte long
        self.peer_id = hashlib.sha1(bytes(random.getrandbits(20))).digest()
        port = 6882
        left = self.file_length

        try:
            response = requests.get(self.announce_url, params={
                'info_hash': self.info_hash,
                'peer_id': self.peer_id,
                'uploaded': 0,
                'downloaded': 0,
                'left': left,
                'port': port,
                'event': 'started',
            })
        except Exception as e:
            print(e, "Too many times", sep='\n')
            return


        data = bcoding.bdecode(response.content)
        self.piece_list = self.add_pieces()
        self.add_peers(data)    

    def add_pieces(self):
        pieces = self.data["info"]["pieces"]
        piece_hashes = [pieces[i: i+20] for i in range(0, len(pieces), 20)]
        return [Piece(i, self.piece_length, hash) for i, hash in enumerate(piece_hashes)]
    
    def add_peers(self, data):
        self.peer_list = [Peer(i, peer) for i, peer in enumerate(data["peers"])]
        self.run_connect()
    
    def run_connect(self):
        while True:
            inp = int(input("Enter: "))
            if(inp == -1):
                return
            try:
                if self.peer_list[inp].connect_to_peer(self.info_hash, self.peer_id):
                    print(self.piece_list[0].n_blocks)
                    self.peer_list[inp].request_piece(self.piece_list[1])
            except Exception as e:
                print(e)
        # -------- Still need to resolve the error in this function --------