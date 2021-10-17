import bcoding
import hashlib
import random
import requests


class Torrent:
    def __init__(self, file_path) -> None:
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
        print(response.content)
