# file: stega.py
# updated by Duncan Fisher
# 11/2/16

import unittest
import os

from PIL import Image

from gif import Gif
from blossom import blossom_perfect_matching



class ByteOperationError(Exception):
	"""
	Base class for exceptions raised in byte injection and extraction operations.

	Attributes:
		operation -- byte operation that caused the error
	"""

	def __init__(self, operation):
		self.operation = operation



def inject_bytes(bs1, bs2, n=2):
	"""
	n = number of bits to store in each byte via lsb substitution

	accepts two bytes objects bs1 and bs2 and injects the bytes of
	bs2 n bits at a time into the least significant bits of each
	byte of bs1. Checks to ensure bs1 is large enough to hold the
	bits of bs2
	"""
	x = 8//n
	if len(bs1) < x*len(bs2) or 8 % n != 0:
		raise ByteOperationError('inject')
	ba = bytearray(bs1)
	for i, byte in enumerate(bs2):
		for j in range(x):
			ba[x*i+j] = (ba[x*i+j] & (255 << n)) | ((byte >> n*(x-1-j)) & (2**n - 1))
	return bytes(ba)

def extract_n_bytes(data, n, b=2):
	"""
	b = number of bits to extract from each byte (lsb)

	returns a bytes object that is n bytes long and consists
	of the least significant bits of data
	"""
	x = 8//b
	if len(data) < x*n or 8 % b != 0:
		raise ByteOperationError('extract')
	ba = bytearray(n)
	for i in range(x*n):
		ba[i//x] = ba[i//x] | ((data[i] & (2**b - 1)) << b*((x-1) - (i%x)))
	return bytes(ba)

def pack(data):
	"""
	appends a 4 byte field specifying the length of data
	"""
	size = len(data).to_bytes(4, byteorder='big')
	return size + data


def unpack(data, n=2):
	"""
	n = number of lsb bits

	parses a bytes object
	returns a tuple with the length and the data segment
	"""
	if 8 % n != 0:
		raise ByteOperationError('unpack')
	x = 8//n
	size = int.from_bytes(extract_n_bytes(data, 4, b=n), byteorder='big')
	data_segment = extract_n_bytes(data[4*x:], size, b=n)
	return size , data_segment


def available_bytes(carrier):
	"""
	returns number of bytes that can be stored inside carrier
	using lsb substitution (2 bits per byte)
	"""
	img = Image.open(carrier)
	img_bytes = img.tobytes()
	return len(img_bytes)//4


def inject_file(carrier, hidden, output):
	"""
	recieves 3 file objects
	stores data from hidden in carrier and saves result to output
	"""
	img = Image.open(carrier)
	hidden_bytes = hidden.read()
	output_bytes = inject_bytes(img.tobytes(), pack(hidden_bytes))
	img = Image.frombytes(img.mode, img.size, output_bytes)
	img.save(output, format='PNG')


def inject_text(carrier, text, output):
	"""
	stores unicode text inside carrier and saves result to output
	"""
	img = Image.open(carrier)
	text_bytes = text.encode()
	output_bytes = inject_bytes(img.tobytes(), pack(text_bytes))
	img = Image.frombytes(img.mode, img.size, output_bytes)
	img.save(output, format='PNG')


def extract_file(carrier, output):
	"""
	given an image with a hidden file
	stores the hidden file in output
	"""
	img = Image.open(carrier)
	length, output_bytes = unpack(img.tobytes())
	output.write(output_bytes)


def extract_text(carrier):
	"""
	given an image with a hidden unicode string
	returns the string
	"""
	img = Image.open(carrier)
	length, text_bytes = unpack(img.tobytes())
	text = text_bytes.decode()
	return text

def gif_inject(gif, data):
	"""
	Injects data into a gif object.
	"""

	packed = pack(data)
	if gif.available_bytes() < len(packed):
		raise ByteOperationError('gif_inject')

	bi = 0
	f = gif.get_frames()
	i = 0
	while bi < len(packed):
		while f[i].local_color_table_flag:
			i += 1
		n = min(f[i].available_bytes(), len(packed) - bi)
		f[i].index_stream = inject_bytes(f[i].index_stream, packed[bi:bi+n], 1)
		bi += n
		i += 1


def gif_extract(gif):
	"""
	Extracts data from a gif object.
	"""
	ba = bytearray()
	for f in gif.get_frames():
		if not f.local_color_table_flag:
			extra = len(f.index_stream) % 8
			print(extra)
			ba += bytearray(f.index_stream[:len(f.index_stream)-extra])

	size, data = unpack(ba, 1)
	return data


class TestByteOperations(unittest.TestCase):

	pantry = bytes(8)
	food = b'\xf0\x0d'
	full_pantry = b'\x03\x03\x00\x00\x00\x00\x03\x01'

	def test_inject_bytes(self):
		self.assertEqual(inject_bytes(self.pantry, self.food), self.full_pantry)
		# test inject too many bytes
		with self.assertRaises(ByteOperationError):
			inject_bytes(self.pantry, self.full_pantry)

	def test_extract_n_bytes(self):
		self.assertEqual(extract_n_bytes(self.full_pantry, 2), self.food)
		# test extract too many bytes
		with self.assertRaises(ByteOperationError):
			extract_n_bytes(self.pantry, 8)

	def test_inject_then_extract_bytes(self):
		# generate random byte strings
		bs1 = os.urandom(128)
		bs2 = os.urandom(32)

		bs3 = inject_bytes(bs1, bs2)
		self.assertEqual(extract_n_bytes(bs3, 32), bs2)

	def test_pack_then_unpack(self):
		bs = os.urandom(32)
		storage = inject_bytes(bytes(4*(len(bs)+4)), pack(bs))
		size, data_segment = unpack(storage)
		self.assertEqual(len(data_segment), size)
		self.assertEqual(data_segment, bs)

class TestGifOperations(unittest.TestCase):

	fnames = ['../gifs/sample_1.gif',
				'../gifs/sample_2_animation.gif',
				'../gifs/Dancing.gif']

	def test_inject_then_extract(self):
		for fname in self.fnames[:2]:
			mygif = Gif()
			mygif.read_from_file(fname)
			b = os.urandom(mygif.available_bytes()-4)
			gif_inject(mygif, b)
			data = gif_extract(mygif)
			print(b.hex())
			print(data.hex())
			self.assertEqual(b, data)



if __name__ == "__main__" :

	unittest.main()
