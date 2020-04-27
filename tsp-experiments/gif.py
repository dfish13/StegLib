
class BadFileError(Exception):
	
	def __init__(self, message):
		self.message = message


class Gif:

	header = 'GIF89a'.encode('utf-8')
	extension_introducer = 0x21
	graphics_control_label = 0xf9
	plain_text_label = 0x01
	application_label = 0xff
	comment_label = 0xfe
	image_separator = 0x2c
	trailer = 0x3b


	def __init__(self):
		pass


	def read_from_file(self, fname):
		gifFile = open(fname, 'rb')
		self.bin = gifFile.read()
		gifFile.close()
		self.pos = 0
		self.size = len(self.bin)
		self._header()
		self._logical_screen_descriptor()
		self._global_color_table()
		self.animation_start = self.pos

	def _header(self):
		if self._read_bin(6) != Gif.header:
			raise BadFileError('Invalid header')

	def _logical_screen_descriptor(self):
		b = self._read_bin(7)
		self.canvas_width = int.from_bytes(b[:2], byteorder='little')
		self.canvas_height = int.from_bytes(b[2:4], byteorder='little')
		self.global_color_table_flag = (b[4] & 128)
		self.color_resolution = (b[4] & 112) >> 4
		self.sort_flag = (b[4] & 8) >> 3
		self.global_color_table_size = 1 << ((b[4] & 7)+1)
		self.background_color_index = b[5]
		self.pixel_aspect_ratio = b[6]

	def _global_color_table(self):
		if not self.global_color_table_flag:
			raise BadFileError('No Global Color Table')
		
		b = self._read_bin(self.global_color_table_size*3)
		self.global_color_table = []
		for i in range(0, self.global_color_table_size*3, 3):
			self.global_color_table.append(tuple(b[i:i+3]))

	def get_frame(self):
		
		self._dispose()
		
		b = _read_bin(1)
		while b[0] != Gif.image_separator:
			if b[0] == Gif.trailer:
				return 0
			elif b[0] == Gif.extension_introducer:
				self._extension()
			else:
				raise BadFileError('No new frame or trailer')
			b = _read_bin(1)
		self._image()

	def _image(self):
		b = _read_bin(9)
		self.frame_x = int.from_bytes(b[:2], byteorder='little')
		self.frame_y = int.from_bytes(b[2:4], byteorder='little')
		self.frame_width = int.from_bytes(b[4:6], byteorder='little')
		self.frame_height = int.from_bytes(b[6:8], byteorder='little')
		self.local_color_table_flag = b[8] & 128
		self.interlace_flag = b[8] & 64
		self.local_color_table_size = 1 >> ((b[8] & 7)+1)
		if self.local_color_table_flag:
			b = self._read_bin(self.local_color_table_size*3)
			self.local_color_table = []
			for i in range(0, self.local_color_table_size*3, 3):
				self.local_color_table.append(tuple(b[i:i+3]))
			self.color_table = self.local_color_table
		else:
			self.color_table = self.global_color_table
		self._image_data()

	def _image_data(self):
		



	def _extension(self):
		b = _read_bin(1)
		if b[0] == Gif.graphics_control_label:
			self._graphics_control_extension()
		elif b[0] == Gif.plain_text_label:
			self._plain_text_extension()
		elif b[0] == Gif.application_label:
			self._application_extension()
		elif b[0] == Gif.comment_label:
			self._comment_extension()
		else:
			raise BadFileError('Unrecognized extension label')


	def _graphics_control_extension(self):
		pass

	def _plain_text_extension(self):
		pass

	def _application_extension(self):
		pass

	def _comment_extension(self):
		pass

	def _trailer(self):
		pass

	def _dispose(self):
		pass

	def _read_bin(self, n):
		b = self.bin[self.pos:self.pos+n]
		if len(b) != n:
			raise BadFileError("Failed to read bytes")
		self.pos += n
		return b

	def rewind():
		pass

	def write_to_file(self, fname):
		pass



