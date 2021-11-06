import requests
from requests.models import Response
from peerleech.parser import Torrent
import json

torrent = Torrent("./peerleech/random.org-pregenerated-2021-10-txt.torrent")
# response = torrent.connect_to_tracker()
torrent.run_connect()
# torrent.add_pieces()
