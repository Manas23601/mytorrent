import requests
from peerleech.parser import Torrent
import json

torrent = Torrent("ubuntu-20.04.3-desktop-amd64.iso.torrent")
response = torrent.get_from_tracker()


