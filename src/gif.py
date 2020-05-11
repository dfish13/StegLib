import unittest

from decode import *


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

class Frame(GifComponent):


	def __str__(self):
		return 'Frame'

	def __init__(self, binary_stream):
		super().__init__('Frame')
		b = binary_stream.read(8)
		self.frame_left = int.from_bytes(b[:2], byteorder='little')
		self.frame_top = int.from_bytes(b[2:4], byteorder='little')
		self.frame_width = int.from_bytes(b[4:6], byteorder='little')
		self.frame_height = int.from_bytes(b[6:], byteorder='little')
		self.packed_byte = binary_stream.read(1)
		self.index_stream = lzw_decompress(code_stream_from_bytes(binary_stream))


class Gif:

	header = 'GIF89a'.encode('utf-8')
	extension_introducer = bytes.fromhex('21')
	image_separator = bytes.fromhex('2C')
	trailer = bytes.fromhex('3B')

	def __str__(self):
		return '\n'.join(str(p) for p in self.components)


	def __init__(self):
		self.components = []


	def read_from_file(self, fname):
		with open(fname, 'rb') as gifFile:
			self._header(gifFile)
			self._logical_screen_descriptor(gifFile)
			self._global_color_table(gifFile)

			while 1:
				b = gifFile.read(1)
				if b == Gif.extension_introducer:
					self.components.append(Extension(gifFile))
				elif b == Gif.image_separator:
					self.components.append(Frame(gifFile))
				elif b == Gif.trailer:
					break
				else:
					raise BadFileError('Unrecognized byte')

	def get_frames(self):
		return [c for c in self.components if c.type == 'Frame']

	def _header(self, gifFile):
		if gifFile.read(6) != Gif.header:
			raise BadFileError('Invalid header')

	def _logical_screen_descriptor(self, gifFile):
		b = gifFile.read(7)
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

	def write_to_file(self, fname):
		pass


class TestGif(unittest.TestCase):
	pass



if __name__ == "__main__" :

	mygif = Gif()
	mygif.read_from_file('../gifs/Dancing.gif')

	print(mygif)
