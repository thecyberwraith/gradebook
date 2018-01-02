import logging

from enum import Enum

class StudentStatus(Enum):
	ACTIVE = 1
	WITHDRAWN = 2
	DROPPED = 3

class StudentName(object):
	keys = ['Last Name', 'First Name', 'Preferred Name']

	def __init__(self, first, last, preferred=None):
		self._first = first
		self._last = last
		self._preferred = preferred
	
	@property
	def first(self):
		return self._first
	
	@property
	def last(self):
		print('Last', self._last, self.last)
		print('First', self._first, self.first)
		return self._last

	@property
	def first_last(self):
		return '{} {}'.format(self.first, self.last)
	
	@property
	def last_first(self):
		return '{}, {}'.format(self.last, self.first)
	
	@property
	def preferred(self):
		first = self.first
		if self._preferred:
			first = self._preferred

		return '{} {}'.format(first, self.last)
	
	@property
	def expanded(self):
		if self._preferred:
			return '{} ({}) {}'.format(
				self.first,
				self._preferred,
				self.last
			)
		else:
			return self.first_last
	
	@staticmethod
	def from_dictionary(dictionary):
		if not (StudentName.keys[0] in dictionary and StudentName.keys[1] in dictionary):
			logging.debug('About to fail at dictionary {}'.format(dictionary))
			raise KeyError('No name could be extracted from the information.')

		preferred_name = ''

		if StudentName.keys[2] in dictionary:
			preferred_name = dictionary[StudentName.keys[2]]

		name = StudentName(
			first = dictionary[StudentName.keys[0]],
			last = dictionary[StudentName.keys[1]],
			preferred = preferred_name
		)
		return name
	
	def to_dictionary(self, dictionary):
		dictionary[StudentName.keys[0]] = self.first
		dictionary[StudentName.keys[1]] = self.last
		dictionary[StudentName.keys[2]] = self._preferred
		
class Student(object):
	'''
	Takes a dictionary of information and puts it all into an object that
	easily manages the data.
	'''

	'''
	The keys required from a dictionary. Also used to export to csv.
	'''
	keys = ['Student ID', 'Email', 'Year', 'Status', 'Major'] + StudentName.keys

	def __init__(self, data):
		'''
		Given a dictionary of data, create a student with the specified
		information. This data should contain the following keys:
			
			First Name
			Last Name
			Student ID
			Email
			Preferred Name
			Year
			Status
			Major
		'''

		for key in Student.keys:
			safe_key = '_{}'.format(key.replace(' ', '_').lower())
			setattr(self, safe_key, data[key])
		self._name = StudentName.from_dictionary(data)
	
	@property
	def name(self):
		return self._name

	@property
	def student_id(self):
		return self._student_id
	
	@property
	def email(self):
		return self._email
	
	@property
	def year(self):
		return self._year
	
	@property
	def status(self):
		return self._status
	
	@status.setter
	def status(self, status):
		self._status = status
	
	@property
	def major(self):
		return self._major

	@property
	def pid(self):
		'''
		Given a student dictionary, take the email for the students and grab
		the PID portion.
		'''
		email = self.email
		return email[:email.find('@')]
	
	def to_dictionary(self):
		'''
		Return a dictionary with keys from Student.keys.
		'''
		data = dict()
		for key in Student.keys:
			data[key] = getattr(self, '_{}'.format(key.replace(' ', '_')).lower())

		return data

	def __str__(self):
		return self.name.expanded
	
	def __repr__(self):
		return str(self)
