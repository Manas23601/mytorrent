import bcoding
import hashlib
import random
import requests
import struct
import socket
class Torrent:
    def __init__(self, file_path):
        try:
            with open(file_path, "rb") as f:
                self.data = bcoding.bdecode(f.read())
        except EnvironmentError as err: # parent of IOError, OSError *and* WindowsError where available
            print(err)

        self.info_hash = hashlib.sha1(bcoding.bencode(self.data["info"])).digest()
    
    def get_peers(self):
        peer_id = hashlib.sha1(bytes(random.getrandbits(20))).digest()
        
        url = self.data["announce"]
        port = 6882
        pieces = [self.data['info']['pieces'][i:i+20] for i in range(0, len(self.data['info']['pieces']), 20)]
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
