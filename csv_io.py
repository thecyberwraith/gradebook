'''
module csv_io

The gradebook program interacts with WebAssign, Canvas, and the user primarily
through CSV files. This module handles the interpretation of CSV files as
Python objects used by the gradebook and vice versa.
'''
import csv

def write_dataset(filename, dataset):
	'''
	Write the given dataset to the specified filename as a tab delimited CSV
	file.

	filename - string
	dataset - an iterable of dictionaries, where the keys are the CSV headers
	'''
	
	headers = None

	for row in dataset:
		headers = row.keys()
		break
	
	with open(filename, 'w') as csv_file:
		writer = csv.DictWriter(csv_file, headers)
		writer.writeheader()
		writer.writerows(dataset)

def load_csv_as_dict(filename):
	'''
	Load the CSV. For each row, let the first entry be the key and the
	remainder of the entry be the payload. Return a dictionary that yields the
	payload for each key. Assumes no header information is provided.
	'''
	dictionary = dict()

	with open(filename, 'r') as csv_file:
		csv_reader = csv.reader(csv_file)

		for row in csv_reader:
			dictionary[row[0]] = row[1:]
	
	return dictionary

class SafeDictionary(object):
	'''
	When reading data from a CSV file, we want the keys read to be case
	insensitive. This allows the code using the SafeDictionary to be more human
	readable, while the values can still be received. Furthermore, iterating
	over the dictionary yields that safe keys that can be used as attributes on
	objects.
	
	Due to the design, this means there will be a clash if the input data has
	keys that reduce to the same string under the make_key_safe method. The
	constructor raises an error in such instances.
	'''
	def __init__(self, data):
		self._safe_to_raw_map = {SafeDictionary.make_key_safe(key): key for key in data}

		if len(self._safe_to_raw_map) < len(data):
			raise KeyError('There is a key clash under the SafeDictionary.make_key_safe method for the dictionary {}'.format(data))

		self._data = data.copy()
	
	@staticmethod
	def make_key_safe(key):
		'''
		Keys should be case insensitive and spaces replaced with underscores. This
		method handles all that, so that the keys listed below can be more human
		readable.
		'''
		return key.replace(' ', '_').lower()
	
	def _get_raw_key(self, key):
		'''
		Get the key from the original data that corresponds to this key.
		'''
		return self._safe_to_raw_map[SafeDictionary.make_key_safe(key)]
	
	def __getitem__(self, key):
		return self._data[self._get_raw_key(key)]
	
	def __contains__(self, key):
		return self._get_raw_key(key) in self._data
	
	def __iter__(self):
		return self._data.__iter__()
	
	def safe_iter(self):
		'''
		Iterate over the keys after converting using make_key_safe
		'''
		for key in self:
			yield SafeDictionary.make_key_safe(key)

def make_safe(function):
	'''
	A decorator to apply on functions that converts all dictionaries to
	SafeDictionaries.
	'''
	def function_with_safe_dictionary(*args, **kw_args):
		new_args = []
		for arg in args:
			if isinstance(arg, dict):
				arg = SafeDictionary(arg)
			new_args.append(arg)
		for key in kw_args:
			if isinstance(kw_args[key], dict):
				kw_args[key] = SafeDictionary(kw_args[key])

		return function(*new_args, **kw_args)

	return function_with_safe_dictionary
