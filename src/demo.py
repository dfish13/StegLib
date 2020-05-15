from gif import Gif
from stega import *
from blossom import blossom_perfect_matching


if __name__ == "__main__":
    message = 'Duncanwashere'.encode('utf-8')
    inFile = '../gifs/Dancing.gif'
    outFile = '../gifs/demo.gif'

    mygif = Gif()
    mygif.read_from_file(inFile)
    mygif.reorder_color_table(blossom_perfect_matching)
    gif_inject(mygif, message)
    mygif.write_to_file(outFile)
    data = gif_extract(mygif)

    print(data.decode('utf-8'))
