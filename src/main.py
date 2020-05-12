import matplotlib.pyplot as plt
import os
import numpy as np
import io

from blossom import blossom_perfect_matching, color_distance
from gif import Gif
from stega import *

def greedy_tsp_3d(gct):
	x_gct = gct.copy()
	color = x_gct[0]
	x_gct.remove(color)
	perm = []
	perm.append(gct.index(color))
	while x_gct:
		min_distance = None
		for xcolor in x_gct:
			d = color_distance(xcolor, color)
			if min_distance is None or d < min_distance:
				min_distance = d
				min_color = xcolor
		color = min_color
		perm.append(gct.index(color))
		x_gct.remove(color)
	return perm

def apply_permutation(perm, color_table, index_stream):
	new_color_table = []
	inv_perm = list.copy(perm)
	for i, x in enumerate(perm):
		new_color_table.append(color_table[x])
		inv_perm[x] = i

	new_index_stream = [inv_perm[x] for x in index_stream]
	return new_color_table, new_index_stream

if __name__ == "__main__":

	inner = '../gifs/sample_2_animation.gif'
	outer = '../gifs/Dancing.gif'

	inner_gif = Gif()
	inner_gif.read_from_file(inner)
	frame = inner_gif.get_frames()[0]
	frame.index_stream = inject_bytes(bytes(frame.index_stream), pack('Duncanwashere'.encode('utf-8')), 1)

	binary_stream = io.BytesIO()
	inner_gif.write_to_stream(binary_stream)

	binary_stream.seek(0)

	outer_gif = Gif()
	outer_gif.read_from_file(outer)
	frame = outer_gif.get_frames()[0]
	frame.index_stream = inject_bytes(bytes(frame.index_stream), pack(binary_stream.read()), 1)




	blossom_perm = blossom_perfect_matching(outer_gif.global_color_table)

	outer_gif.global_color_table, frame.index_stream = apply_permutation(blossom_perm, outer_gif.global_color_table, frame.index_stream)

	outer_gif.write_to_file('../gifs/gifsallthewaydown.gif')

	plt.imshow(outer_gif.get_images()[0])
	plt.show()
