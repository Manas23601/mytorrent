import hashlib
import math

class Piece: 
    def __init__(self, index, size, hash):
        self.index = index
        self.size = size
        self.n_blocks = math.ceil(self.size / (2**14))

        self.hash = hash
        self.assigned = False
        self.verified = False

        self.blocks = [[i*(2**14), (i+1)*(2**14), b''] for i in range(self.n_blocks)]
        self.blocks[-1][1] = self.size