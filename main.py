import requests
from peerleech.parser import Torrent

torrent = Torrent("ubuntu-20.04.3-desktop-amd4.iso.torrent")
torrent.get_peers()


