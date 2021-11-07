import bcoding
import hashlib
import random
import requests
import struct
import socket
import os
from math import ceil
from bitstring import BitArray

from requests.models import LocationParseError

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
        # url of tracker
        self.announce_url = self.data["announce"]
        # each piece size in file
        self.piece_length = self.data["info"]["piece length"]
        # total file length
        self.file_length = 0

        # for multi file torrent
        if self.data["info"].get("files"):
            folder = "download"
            if self.data.get("title"):
                folder = self.data["title"]
                path = os.path.join(os.getcwd(), folder)
                if not os.path.isdir(path):
                    os.mkdir(path)
            for file in self.info["files"]:
                self.file_length += file["length"]

        else:
            self.file_length = self.data["info"]["length"]

        # piece objects declared with block count and piece hash
        self.add_pieces()
    
    def print_all_information(self):
        for piece in self.pieces:
            print(piece.index, piece.hash, piece.size)

    def add_pieces(self):
            # hash value of pieces
        self.piece_hashs = [self.data['info']['pieces'][i:i+20] for i in range(0, len(self.data['info']['pieces']), 20)]
        self.pieces = [Piece(i, self.piece_length, hash) for i, hash in enumerate(self.piece_hashs)]

        self.num_of_pieces = ceil(self.file_length / self.piece_length)
        last_piece_size = int(self.file_length % self.piece_length)
        if last_piece_size > 0:
            self.pieces[-1].size = last_piece_size


    #make a get request to the tracker to fetch the peer ips
    def connect_to_tracker(self):
        # 20 byte long
        self.peer_id = hashlib.sha1(bytes(random.getrandbits(20))).digest()
        # print(self.peer_id)
        self.peers = []
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
        self.tracker_interval = data["interval"]
        # print(data)
        self.add_peers(data)    

    
    def add_peers(self, data):

        if isinstance(data["peers"], list):
            self.peer_list = [Peer(i, peer["ip"], peer["port"], peer["peer id"]) for i, peer in enumerate(data["peers"])]
        #if tracker responds in compact form
        else:
            peers = [data["peers"][i:i+6] for i in range(0, len(data["peers"]), 6)]
            self.peer_list = [Peer(i, peer[0:4], peer[4:], None) for i, peer in enumerate(peers)]
        
        print("All peers")
        for peer in self.peer_list:
            print(peer.ip , peer.port)
        # self.run_connect()
    
    def run_connect(self):
        self.peer_id = b"\xc3@#\x90\xda\xb7\x1f\xb9\x06B\xd5.\xf0wH'\xefw\xfe\r"
        self.peer_list = []
        self.peer_list.append(Peer(0,'79.141.154.97',51413,"manas"))
        while True:
            inp = int(input("Enter: "))
            if(inp == -1):
                return
            try:
                if not self.peer_list[inp].connect_to_peer(self.info_hash, self.peer_id):
                    print("Handshake Succesful")
                    self.peer_list[inp].recieve_message(self.pieces)
            except Exception as e:
                print(e)
        # -------- Still need to resolve the error in this function --------