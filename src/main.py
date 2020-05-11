import matplotlib.pyplot as plt
import numpy as np

from blossom import blossom_perfect_matching, color_distance

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

if __name__ == "__main__":
	fname = '../gifs/Dancing.gif'

	with open(fname, 'rb') as gif:
		b = gif.read(6)
		print('header = {}'.format(b.decode('utf-8')))
		b = gif.read(7)
		canvas_width = int.from_bytes(b[:2], byteorder='little')
		canvas_height = int.from_bytes(b[2:4], byteorder='little')
		global_color_table_flag = (b[4] & 128) >> 7
		color_resolution = (b[4] & 112) >> 4
		sort_flag = (b[4] & 8) >> 3
		global_color_table_size = 2**((b[4] & 7)+1)


		print('width = {}, height = {}'.format(canvas_width, canvas_height))
		print('global color table flag = {}'.format(global_color_table_flag))
		print('color resolution = {}'.format(color_resolution))
		print('sort flag = {}'.format(sort_flag))
		print('size of global color table = {}'.format(global_color_table_size))

		global_color_table = []
		if global_color_table_flag:
			for i in range(global_color_table_size):
				b = gif.read(3)
				global_color_table.append(tuple(b))

	# display color table
	cell_width, cell_height = (5, 100)

	perfect_matching_gct = blossom_perfect_matching(global_color_table)

	colors_img = []

	for i in range(5):
		for c in perfect_matching_gct:
			colors_img += list(c)

	plt.imshow(np.asarray(colors_img).reshape(5, len(perfect_matching_gct), 3))
	plt.show()
