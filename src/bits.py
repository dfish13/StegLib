import math

class Bits:

    def __init__(self):
        self.b = bytearray()
        self.num_bits = 0
        self.start = 0

    def __init__(self, n, num_bits):
        mbytes = n.to_bytes(math.ceil(num_bits/8), byteorder='big')
        self.start = len(mbytes)*8 - num_bits
        self.b = bytearray(mbytes)
        self.num_bits = num_bits

    def get_bytearray(self):
        return self.b

    def __getitem__(self, i):
        if i >= self.num_bits or i < 0:
            raise IndexError()
        bi = (self.start + i)//8
        offset = (self.start + i) % 8
        mask = 1 << (7 - offset)
        if mask & self.b[bi]:
            return 1
        else:
            return 0


if __name__ == "__main__":
    bits = Bits(300, 13)

    for i in range(13):
        print(bits[i])

    print(bits.get_bytearray())
