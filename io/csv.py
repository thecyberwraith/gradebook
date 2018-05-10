import csv

def read_rows_from_source(source):
	'''
	Plainly reads rows from given source with no validation.
	'''
	data = []

	reader = csv.reader(source)
	for row in reader:
		data.append(row)
	
	return data

def read_dict_from_source(source, headers=None):
	'''
	Reads rows from a source as a dictionary with header being an ordered
	list of keys. If header is none, it is assumed that the first line provides
	the headers. If any value returns None, raise a KeyError exception.

	Note: If there is more columns than headers in a row, then remaining data
	is truncated.
	'''
	data = []

	reader = csv.DictReader(source, fieldnames=headers)
	for row in reader:
		for key in row:
			if row[key] is None:
				raise KeyError('Failed to grab field {} from csv source {} at row {}'.format(key, source, row))
		data.append(row)
	
	return data

def write_dict(destination, headers, dictionaries):
	'''
	Write dictionaries to the destination file-like object.
	'''
	writer = csv.DictWriter(destination, headers)
	writer.writeheader()
	writer.writerows(dictionaries)
