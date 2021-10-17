import bcoding
import hashlib
import random
import requests

# open the torrent files
f = open("./ubuntu-20.04.3-desktop-amd64.iso.torrent", "rb")
# decode
torrent = bcoding.bdecode(f.read())


# info hash
info_hash = hashlib.sha1(bcoding.bencode(torrent["info"])).digest()


#peer id
peer_id = hashlib.sha1(bytes(random.getrandbits(20))).digest()

#for get response
port = 6882
uploaded = "0"
downloaded = "0"
left = "1"
url = torrent["announce"]
pieces = [torrent['info']['pieces'][i:i+20] for i in range(0, len(torrent['info']['pieces']), 20)]
downloaded = len(pieces) * torrent["info"]['piece length']

response = requests.get(url, params={
            'info_hash': info_hash,
            'peer_id': peer_id,
            'uploaded': 0,
            'downloaded': downloaded,
            'left': 0,
            'port': port,
            'event': 'started',
        })
print(response.content)
