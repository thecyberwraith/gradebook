from io import StringIO
from unittest import TestCase

from gradebook.io.csv import *


class TestCSVReadRows(TestCase):
	def test_even_rows(self):
		source = StringIO('1,2,3\n4,5,6\n7,8,9')

		result = read_rows_from_source(source)
	
		self.assertEqual(3, len(result), 'Incorrect number of rows returned from method')
		for row in result:
			self.assertEqual(3, len(row), 'Row contained incorrect number of items.')
	
	def test_uneven_rows(self):
		source = StringIO('1\n"potato",9\n"a","b","c"')

		result = read_rows_from_source(source)

		self.assertEqual(3, len(result), 'Incorrect number of rows returned from method')
		for i, row in enumerate(result):
			self.assertEqual(i+1, len(row), 'Row conatined incorrect number of items.')

class TestCSVReadDict(TestCase):
	def test_headed_read(self):
		source = StringIO('a,b,23,"d"\n1,2,3,4\n5,6,7,8')

		result = read_dict_from_source(source, headers=None)
		
		self.assertEqual(2, len(result))
		d = result[0]
		self.assertEqual({'a','b','23','d'}, d.keys())
	
	def test_headless_read(self):
		source = StringIO('1,2,3,4\n5,6,7,8')
		headers = 'a','b','23',5

		result = read_dict_from_source(source, headers=headers)
		
		self.assertEqual(2, len(result))
		self.assertEqual(set(headers), result[0].keys())
	
	def test_exception_when_too_few_fields(self):
		source = StringIO('1,2,3\n1,2')
		headers = 'a','b','c','d'

		with self.assertRaises(KeyError):
			read_dict_from_source(source, headers=headers)

class TestCSVWriteDict(TestCase):
	def test_write_correctly(self):
		test_data = [{'a':1, 1:3}, {1:4,'a':'b'}]
		destination = StringIO()

		write_dict(destination, [1, 'a'], test_data)

		destination.seek(0)

		correct_output = ['1,a','3,1', '4,b']
		output = [s.strip() for s in destination.readlines()]

		self.assertEqual(correct_output, output)
