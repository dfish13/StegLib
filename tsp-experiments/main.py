from graphics import *
import math
import sys

def color_distance(c1, c2):
	return (c1[0] - c2[0])**2 + (c1[1] - c2[1])**2 + (c1[2] - c2[2])**2

def greedy_tsp_3d(gct):
	x_gct = gct.copy()
	color = x_gct[0]
	x_gct.remove(color)
	new_gct = [color]
	while x_gct:
		min_distance = None
		for xcolor in x_gct:
			if min_distance is None:
				min_distance = color_distance(xcolor, color)
				min_color = xcolor
			elif color_distance(xcolor, color) < min_distance:
				min_distance = color_distance(xcolor, color)
				min_color = xcolor
		new_gct.append(min_color)
		color = min_color
		x_gct.remove(color)
	return new_gct


fname = '../gifs/supersaiyan.gif'

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

tsp_global_color_table = greedy_tsp_3d(global_color_table)

win = GraphWin('Original Color Table', cell_width*global_color_table_size, cell_height)
win2 = GraphWin('Greedy TSP Sorted Table', cell_width*global_color_table_size, cell_height)

for i in range(global_color_table_size):
	p1 = Point(cell_width*i, 0)
	p2 = Point(cell_width*(i+1), cell_height)
	rec  = Rectangle(p1, p2)
	rec.setFill(color_rgb(*global_color_table[i]))
	rec.setOutline(color_rgb(*global_color_table[i]))
	rec.draw(win)

for i in range(global_color_table_size):
	p1 = Point(cell_width*i, 0)
	p2 = Point(cell_width*(i+1), cell_height)
	rec  = Rectangle(p1, p2)
	rec.setFill(color_rgb(*tsp_global_color_table[i]))
	rec.setOutline(color_rgb(*tsp_global_color_table[i]))
	rec.draw(win2)

input()
