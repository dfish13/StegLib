


def lzw_compress(min_code_size, index_stream):
	"""
	Args: Index stream
	Returns: Code stream
	"""
	code_table = {}
	code_size = min_code_size
	clear = 1 << code_size
	stop = clear + 1
	
	# initialize code table
	for i in range(1 << code_size):
		code_table[i] = (i,)

	# start by sending clear code
	code_stream = []
	code_stream.append(clear)

	# begin reading index stream
	for i in index_stream:
		print(i)

	for x in code_table.items():
		print(x)

	return clear




	pass

def lzw_decompress():
	pass



color_table = [(255, 255, 255), (255, 0, 0), (0, 0, 255), (0, 0, 0)]
width = 10
height = 10
image_data = bytes.fromhex('02168C2D99872A1CDC33A00275EC95FAA8DE608C04914C0100')
index_stream = [1, 1, 1, 1, 1, 2, 2, 2, 2, 2,
				1, 1, 1, 1, 1, 2, 2, 2, 2, 2,
				1, 1, 1, 1, 1, 2, 2, 2, 2, 2,
				1, 1, 1, 0, 0, 0, 0, 2, 2, 2,
				1, 1, 1, 0, 0, 0, 0, 2, 2, 2,
				2, 2, 2, 0, 0, 0, 0, 1, 1, 1,
				2, 2, 2, 0, 0, 0, 0, 1, 1, 1,
				2, 2, 2, 2, 2, 1, 1, 1, 1, 1,
				2, 2, 2, 2, 2, 1, 1, 1, 1, 1,
				2, 2, 2, 2, 2, 1, 1, 1, 1, 1,]



lzw_compress(2, index_stream)

