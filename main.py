import requests
from peerleech.parser import Torrent
import json

torrent = Torrent("./peerleech/SuicideQueen_archive.torrent")
response = torrent.connect_to_tracker()


