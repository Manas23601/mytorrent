import hashlib
import math

class Piece: index, size, hash):
        self.index = index
    def __init__(self,
        self.size = size
        self.n_pieces = math.ceil(self.size / (2**14))

        self.hash = hash
        self.assigned = False
        self.verified = False

        self.pieces = [[i*(2**14), (i+1)*(2**14), b''] for i in range(self.n_pieces)]
        self.pieces[-1][1] = self.size