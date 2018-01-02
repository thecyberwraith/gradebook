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
