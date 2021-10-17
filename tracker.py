pieces = [torrent['info']['pieces'][i:i+20] for i in range(0, len(torrent['info']['pieces']), 20)]

