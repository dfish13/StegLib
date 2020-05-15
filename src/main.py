import matplotlib.pyplot as plt
import os
import numpy as np
import io

from blossom import blossom_perfect_matching
from gif import Gif
from stega import *

if __name__ == "__main__":

	inner = '../gifs/sample_2_animation.gif'
	outer = '../gifs/Dancing.gif'

	inner_gif = Gif()
	inner_gif.read_from_file(inner)
	gif_inject(inner_gif, 'Duncanwashere'.encode('utf-8'))

	binary_stream = io.BytesIO()
	inner_gif.write_to_stream(binary_stream)
	binary_stream.seek(0)

	outer_gif = Gif()
	outer_gif.read_from_file(outer)
	outer_gif.reorder_color_table(blossom_perfect_matching)
	gif_inject(outer_gif, binary_stream.read())

	outer_gif.write_to_file('../gifs/gifception.gif')

	plt.imshow(outer_gif.get_images()[0])
	plt.show()
