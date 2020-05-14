import unittest
import matplotlib.pyplot as plt
import numpy as np
import itertools
import io


class BadFileError(Exception):

	def __init__(self, message):
		self.message = message


def discard_sub_blocks(binary_stream):
	block_size = int.from_bytes(binary_stream.read(1), byteorder='big')
	while block_size > 0:
		binary_stream.seek(block_size, 1)
		block_size = int.from_bytes(binary_stream.read(1), byteorder='big')
	return binary_stream.seek(0, 1)


class GifComponent:

	def __init__(self, t):
		self.type = t


class Extension(GifComponent):

	labels = dict()
	labels[bytes.fromhex('F9')] = 'Graphics'
	labels[bytes.fromhex('01')] = 'Plain Text'
	labels[bytes.fromhex('FF')] = 'Application'
	labels[bytes.fromhex('FE')] = 'Comment'

	def __str__(self):
		return '{} Extension'.format(Extension.labels.get(self.label, 'unknown'))

	def __init__(self, binary_stream):
		super().__init__('Extension')
		self.label = binary_stream.read(1)
		start = binary_stream.seek(0, 1)
		end = discard_sub_blocks(binary_stream)
		binary_stream.seek(start)
		self.sub_blocks = binary_stream.read(end-start)

	def write_to_stream(self, binary_stream):
		binary_stream.write(self.label)
		binary_stream.write(self.sub_blocks)


class Frame(GifComponent):


	def available_bytes(self):
		return len(self.index_stream)//8

	def write_to_stream(self, binary_stream):
		binary_stream.write(self.image_descriptor)
		if self.local_color_table_flag:
			binary_stream.write(bytes(itertools.chain.from_iterable(self.local_color_table)))
		binary_stream.write(self.code_size)
		binary_stream.write(self._compress_index_stream())

	def __str__(self):
		return 'Frame'

	def __init__(self, binary_stream):
		super().__init__('Frame')
		b = binary_stream.read(9)
		self.image_descriptor = b
		self.frame_left = int.from_bytes(b[:2], byteorder='little')
		self.frame_top = int.from_bytes(b[2:4], byteorder='little')
		self.frame_width = int.from_bytes(b[4:6], byteorder='little')
		self.frame_height = int.from_bytes(b[6:8], byteorder='little')
		self.local_color_table_flag = b[8] & 128
		self.interlace_flag = b[8] & 64
		self.sort_flag = b[8] & 32
		self.local_color_table_size = (b[8] & 7) + 1
		if self.local_color_table_flag:
			self._local_color_table(gifFile)
		self._image_data(binary_stream)

	def _local_color_table(self, gifFile):
		self.local_color_table = []
		for i in range(0, self.local_color_table_size):
			self.local_color_table.append(tuple(gifFile.read(3)))

	def _code_stream(self):
		"""
		code stream generator (does not return a list)
		"""
		code_table = dict()
		clear = 1 << self.code_size[0]
		stop = clear + 1
		next_code = stop + 1

		for i in range(clear):
			code_table[(i,)] = i

		index_buffer = (self.index_stream[0],)

		yield clear

		for i in self.index_stream[1:]:
			if (code_table.get(index_buffer + (i,), -1) != -1):
				index_buffer += (i,)
			else:
				code_table[index_buffer + (i,)] = next_code
				yield code_table[index_buffer]
				if next_code == 2**12:
					yield clear
					code_table.clear()
					for j in range(clear):
						code_table[(j,)] = j
					next_code = stop + 1
				else:
					next_code += 1

				index_buffer = (i,)

		yield code_table[index_buffer]
		yield stop

	def _compress_index_stream(self):
		code_size = self.code_size[0]
		clear = 1 << code_size
		stop = clear + 1
		code_size += 1
		init_code_size = code_size
		num_codes = stop + 1

		stream_gen = self._code_stream()
		ba = bytearray()
		sub_block = bytearray()
		b = next(stream_gen).to_bytes(2, byteorder='big')
		if code_size > 8:
			sub_block.append(b[1])
			byte = b[0]
		else:
			byte = b[1]
		shift = code_size
		for c in stream_gen:
			bits_written = 0
			while bits_written < code_size:
				rpad = (shift + bits_written) % 8
				if rpad == 0:
					byte &= (1 << 8) - 1
					sub_block.append(byte)
					if len(sub_block) == 254:
						ba += bytearray([254]) + sub_block
						sub_block = bytearray()
					byte = 0
				byte |= ((c >> bits_written) << rpad)
				frag_size = min(8 - rpad, code_size - bits_written)
				#print('rpad = {}, frag_size = {}, code_size = {}'.format(rpad, frag_size, code_size))
				bits_written += frag_size
			shift = (shift + code_size) % 8
			if num_codes == (1 << code_size) and code_size < 12:
				code_size += 1
			if c == clear:
				code_size = init_code_size
				num_codes = stop
			num_codes += 1

		if shift != 0:
			sub_block.append(byte)
		if len(sub_block) > 0:
			ba += bytearray([len(sub_block)]) + sub_block
		ba.append(0)

		return bytes(ba)

	def _image_data(self, gifFile):
		self.index_stream = []
		self.code_size = gifFile.read(1)
		start = gifFile.seek(0, 1)
		code_size = int.from_bytes(self.code_size, byteorder='big')
		clear = 1 << code_size
		stop = clear + 1
		code_size += 1
		init_code_size = code_size
		self.byte = self.sub_len = self.shift = 0

		self.code_stream = []

		prevCode = self._get_code(gifFile, code_size)
		self.code_stream.append(prevCode)
		if prevCode != clear:
			raise BadFileError('Image data does not begin with clear code')

		code_table = [(i,) for i in range(stop + 1)]
		prevCode = clear
		while 1:
			code = self._get_code(gifFile, code_size)
			self.code_stream.append(code)
			if code == clear:
				code_table = [(i,) for i in range(stop + 1)]
				code_size = init_code_size
				prevCode = code
				continue
			elif code == stop:
				break
			elif code < len(code_table):
				index_list = code_table[code]
				for i in index_list:
					self.index_stream.append(i)
				k = index_list[0]
			else:
				index_list = code_table[prevCode]
				k = index_list[0]
				for i in index_list:
					self.index_stream.append(i)
				self.index_stream.append(k)
			if prevCode != clear:
				code_table.append(code_table[prevCode] + (k,))
			if len(code_table) == (1 << code_size) and code_size < 12:
				code_size += 1
			prevCode = code

		# Should be one more zero byte
		gifFile.read(1)
		end = gifFile.seek(0, 1)
		gifFile.seek(start)
		self.compressed_index_stream = gifFile.read(end-start)


	def _get_code(self, gifFile, code_size):
		code = bits_read = 0
		while bits_read < code_size:
			rpad = (self.shift + bits_read) % 8
			if rpad == 0:
				# Update byte
				if self.sub_len == 0:
					self.sub_len = int.from_bytes(gifFile.read(1), byteorder='big')
				self.byte = int.from_bytes(gifFile.read(1), byteorder='big')
				self.sub_len -= 1
			frag_size = min(code_size - bits_read, 8 - rpad)
			code = code | ((self.byte >> rpad) << bits_read)
			bits_read += frag_size
		code = code & ((1 << code_size) - 1)
		self.shift = (self.shift + code_size) % 8
		return code


class Gif:

	header = 'GIF89a'.encode('utf-8')
	extension_introducer = bytes.fromhex('21')
	image_separator = bytes.fromhex('2C')
	trailer = bytes.fromhex('3B')

	def available_bytes(self):
		return sum(len(f.index_stream) for f in self.get_frames())//8

	def __str__(self):
		return '\n'.join(str(p) for p in self.components)


	def __init__(self):
		self.components = []


	def read_from_file(self, fname):
		with open(fname, 'rb') as gifFile:
			self.read_from_stream(gifFile)

	def read_from_stream(self, binary_stream):
		self._header(binary_stream)
		self._logical_screen_descriptor(binary_stream)
		self._global_color_table(binary_stream)

		while 1:
			b = binary_stream.read(1)
			if b == Gif.extension_introducer:
				self.components.append(Extension(binary_stream))
			elif b == Gif.image_separator:
				self.components.append(Frame(binary_stream))
			elif b == Gif.trailer:
				break
			else:
				raise BadFileError('Unrecognized byte')

	def write_to_file(self, fname):
		with open(fname, 'wb') as gifFile:
			self.write_to_stream(gifFile)

	def write_to_stream(self, binary_stream):
		binary_stream.write(Gif.header)
		binary_stream.write(self.logical_screen_descriptor)
		binary_stream.write(bytes(itertools.chain.from_iterable(self.global_color_table)))
		for c in self.components:
			if c.type == 'Extension':
				binary_stream.write(Gif.extension_introducer)
			elif c.type == 'Frame':
				binary_stream.write(Gif.image_separator)
			c.write_to_stream(binary_stream)
		binary_stream.write(Gif.trailer)

	def get_frames(self):
		return [c for c in self.components if c.type == 'Frame']

	def get_images(self):
		imgs = []
		for f in self.get_frames():
			color_table = f.local_color_table if f.local_color_table_flag else self.global_color_table
			imgs.append(np.asarray(list(itertools.chain.from_iterable(color_table[i] for i in f.index_stream))).reshape(f.frame_height, f.frame_width, 3))
		return imgs

	def _header(self, gifFile):
		if gifFile.read(6) != Gif.header:
			raise BadFileError('Invalid header')

	def _logical_screen_descriptor(self, gifFile):
		b = gifFile.read(7)
		self.logical_screen_descriptor = b
		self.canvas_width = int.from_bytes(b[:2], byteorder='little')
		self.canvas_height = int.from_bytes(b[2:4], byteorder='little')
		self.global_color_table_flag = (b[4] & 128)
		self.color_resolution = (b[4] & 112) >> 4
		self.sort_flag = (b[4] & 8) >> 3
		self.global_color_table_size = 1 << ((b[4] & 7)+1)
		self.background_color_index = b[5]
		self.pixel_aspect_ratio = b[6]

	def _global_color_table(self, gifFile):
		if not self.global_color_table_flag:
			raise BadFileError('No Global Color Table')

		b = gifFile.read(self.global_color_table_size*3)
		self.global_color_table = []
		for i in range(0, self.global_color_table_size*3, 3):
			self.global_color_table.append(tuple(b[i:i+3]))


class TestGif(unittest.TestCase):

	fnames = ['../gifs/sample_1.gif',
	 			'../gifs/sample_2_animation.gif',
				'../gifs/Dancing.gif']

	def test_compress_index_stream(self):
		self.maxDiff = None
		for fname in self.fnames:
			mygif = Gif()
			mygif.read_from_file(fname)
			frame = mygif.get_frames()[0]
			self.assertEqual(frame.compressed_index_stream, frame._compress_index_stream())

	def test_code_stream(self):
		self.maxDiff = None
		for fname in self.fnames:
			mygif = Gif()
			mygif.read_from_file(fname)
			frame = mygif.get_frames()[0]
			self.assertListEqual(frame.code_stream[:4000], list(frame._code_stream())[:4000])



if __name__ == "__main__" :


	unittest.main()
