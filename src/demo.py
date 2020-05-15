from gif import Gif
from stega import *


if __name__ == "__main__":
    fname = '../gifs/demo.gif'

    mygif = Gif()
    mygif.read_from_file(fname)

    data = gif_extract(mygif)

    print(data.decode('utf-8'))
