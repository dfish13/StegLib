from gif import Gif
from stega import *


if __name__ == "__main__":
    fname = '../gifs/demo.gif'

    mygif = Gif()
    mygif.read_from_file(fname)

    size, data = unpack(bytes(mygif.get_frames()[0].index_stream), 1)

    print(data.decode('utf-8'))
