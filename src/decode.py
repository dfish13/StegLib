import matplotlib.pyplot as plt
import numpy as np
import io
import os

from blossom import blossom_perfect_matching
from stega import *
from main import greedy_tsp_3d

def lzw_compress(min_code_size, index_stream):
	"""
	Args: Index stream
	Returns: Code stream
	"""
	code_table = dict()
	code_size = min_code_size
	clear = 1 << code_size
	stop = clear + 1
	next_code = stop + 1

	# initialize code table
	for i in range(1 << code_size):
		code_table[(i,)] = i

	# initialize index buffer
	index_buffer = (index_stream[0],)

	# start by sending clear code
	code_stream = []
	code_stream.append(clear)

	# begin reading index stream
	for i in index_stream[1:]:
		if (code_table.get(index_buffer + (i,), -1) != -1):
			index_buffer += (i,)
		else:
			code_table[index_buffer + (i,)] = next_code
			next_code += 1
			code_stream.append(code_table[index_buffer])
			index_buffer = (i,)

	# print out codes and their corresponding lists of indices
	"""
	code_list = [(v, k) for k, v in code_table.items()]
	code_list.sort(key = lambda x: x[0])
	for code, indexes in code_list:
	print('code = {}, color index(es) = {}'.format(code, indexes))
	"""
	# output code for contents of index buffer
	code_stream.append(code_table[index_buffer])

	# output end of information code
	code_stream.append(stop)

	return code_stream

def lzw_decompress(code_stream):
	"""
	Args: Code stream
	Returns: Index stream
	"""
	# initialize code table
	code_table = []
	clear = code_stream[0]
	stop = clear + 1
	next_code = stop + 1

	for i in range(next_code):
		code_table.append((i,))

	index_stream = []

	prevCode = code_stream[1]
	for c in code_table[prevCode]:
		index_stream.append(c)

	for code in code_stream[2:]:
		if code == clear:
			next_code = stop + 1
			code_table = code_table[:next_code]
			prevCode = code
			continue
		elif code == stop:
			break
		if code < next_code:
			index_list = code_table[code]
			for c in index_list:
				index_stream.append(c)
			if prevCode != clear:
				code_table.append(code_table[prevCode] + (index_list[0],))
				next_code += 1
		else:
			index_list = code_table[prevCode]
			for c in index_list:
				index_stream.append(c)
			index_stream.append(index_list[0])
			code_table.append(index_list + (index_list[0],))
			next_code += 1
		prevCode = code
	return index_stream

def code_stream_to_bytes(min_code_size, code_stream):
	pass


def code_stream_from_bytes(gif):
	keys = []
	key_size = int.from_bytes(gif.read(1), byteorder='big')
	print(key_size)
	clear = 1 << key_size
	stop = clear + 1
	key_size += 1
	init_key_size = key_size
	sub_len = shift = 0

	(key, sub_len, shift, byte) = get_key(gif, key_size, sub_len, shift, 0)
	keys.append(key)
	print(key)

	next_code = stop
	while 1:
		if key == clear:
			key_size = init_key_size
			next_code = stop
		(key, sub_len, shift, byte) = get_key(gif, key_size, sub_len, shift, byte)
		keys.append(key)
		if key == clear:
			continue
		if key == stop:
			break
		if next_code == (1 << key_size) - 1 and key_size < 12:
			key_size += 1
		next_code += 1
	return keys


def get_key(gif, key_size, sub_len, shift, byte):
	key = bits_read = 0
	while bits_read < key_size:
		rpad = (shift + bits_read) % 8
		if rpad == 0:
			# Update byte
			if sub_len == 0:
				sub_len = int.from_bytes(gif.read(1), byteorder='big')
			byte = int.from_bytes(gif.read(1), byteorder='big')
			sub_len -= 1
		frag_size = min(key_size - bits_read, 8 - rpad)
		key = key | ((byte >> rpad) << bits_read)
		bits_read += frag_size
	key = key & ((1 << key_size) - 1)
	shift = (shift + key_size) % 8
	return (key, sub_len, shift, byte)


def discard_sub_blocks(gif):
	block_size = int.from_bytes(gif.read(1), byteorder='big')
	while block_size > 0:
		gif.read(block_size)
		block_size = int.from_bytes(gif.read(1), byteorder='big')

def discard_extension(gif):
	b = gif.read(1)
	if b == bytes.fromhex('F9'):
		print('graphics extension')
		discard_sub_blocks(gif)
	elif b == bytes.fromhex('01'):
		print('plain text extension')
		discard_sub_blocks(gif)
	elif b == bytes.fromhex('FF'):
		print('application extension')
		discard_sub_blocks(gif)
	elif b == bytes.fromhex('FE'):
		print('comment extension')
		discard_sub_blocks(gif)
	else:
		print('could not identify extension')

def apply_permutation(perm, color_table, index_stream):
	new_color_table = []
	inv_perm = list.copy(perm)
	for i, x in enumerate(perm):
		new_color_table.append(color_table[x])
		inv_perm[x] = i

	new_index_stream = [inv_perm[x] for x in index_stream]
	return new_color_table, new_index_stream



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

		while 1:
			b = gif.read(1)
			if b == bytes.fromhex('21'):
				print('discarding extension')
				discard_extension(gif)
			elif b == bytes.fromhex('2C'):
				print('image descriptor block')
				b = gif.read(8)
				img_left = int.from_bytes(b[:2], byteorder='little')
				img_top = int.from_bytes(b[2:4], byteorder='little')
				img_width = int.from_bytes(b[4:6], byteorder='little')
				img_height = int.from_bytes(b[6:], byteorder='little')
				packed_byte = gif.read(1)
				print(packed_byte)
				keys = code_stream_from_bytes(gif)
			if b == bytes.fromhex('3B'):
				print('reached end of file')
				break



	index_stream = lzw_decompress(keys)

	reordering = list(np.random.permutation(global_color_table_size))

	new_color_table, new_index_stream = apply_permutation(reordering, global_color_table, index_stream)

	available = len(new_index_stream)//8
	print('number of free bytes available: {}'.format(available))

	random_bytes = os.urandom(available-4)
	packed_data = pack(random_bytes)

	stega_index_stream = inject_bytes(bytes(new_index_stream), packed_data, n=1)

	size, data = unpack(stega_index_stream, n=1)

	if data == random_bytes:
		print('data are equal')


	mygif2 = []
	for i in stega_index_stream:
		mygif2 += list(new_color_table[i])


	plt.imshow(np.asarray(mygif2).reshape(img_height, img_width, 3))
	plt.show()
