from gif import Gif

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


if __name__ == "__main__":

	fname = '../gifs/sample_2_animation.gif'

	mygif = Gif()
	mygif.read_from_file(fname)

	print('available bytes in first frame = {}'.format(mygif.get_frames()[0].available_bytes()))
	print('total available bytes = {}'.format(mygif.available_bytes()))
