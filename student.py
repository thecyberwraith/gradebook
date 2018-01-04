from enum import Enum
import logging

from csv_io import SafeDictionary, make_safe

class StoredEnum(Enum):
	'''
	Subclasses of this Enum should have upper case enum items. Then loading and
	saving to a dictionary is handled by this class instead of children
	classes. Assumes one value of child is UNDEFINED=0
	'''

	@classmethod
	@make_safe
	def from_dictionary(cls, safe_dictionary):
		key = cls.get_key()
		if key in safe_dictionary and safe_dictionary[key] != '':
			enum_name = safe_dictionary[key].upper()
			# To ignore honors, try this
			enum_name = enum_name.split(' ')[0]
			
			try:
				return cls[enum_name]
			except KeyError:
				raise KeyError('Value {} is not a valid {}'.format(
					enum_name,
					cls
				))

			return cls[safe_dictionary[key].upper()]
		else:
			return cls.UNDEFINED
	
	def to_dictionary(self, dictionary):
		if self.value == 0: # Undefined
			raise ValueError('Cannot save an undefined value.')
		dictionary[self.__class__.get_key()] = self.name
	
	@classmethod
	def get_key(cls):
		'''
		Overridden to provide class specific keys.
		'''
		return None
	
class StudentStatus(StoredEnum):
	UNDEFINED = 0
	ACTIVE = 1
	WITHDRAWN = 2
	DROPPED = 3

	@classmethod
	def get_key(self):
		return 'Status'

class StudentYear(StoredEnum):
	UNDEFINED = 0
	FRESHMAN = 1
	SOPHOMORE = 2
	JUNIOR = 3
	SENIOR = 4 

	@classmethod
	def get_key(self):
		return 'Year'

class StudentName(object):
	keys = ['Last Name', 'First Name', 'Preferred']

	@make_safe
	def __init__(self, first, last, preferred=None):
		self._first = first
		self._last = last
		self._preferred = preferred
	
	@property
	def first(self):
		return self._first
	
	@property
	def last(self):
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
	
	def __str__(self):
		return self.expanded

	def __repr__(self):
		return 'StudentName({})'.format(self)

	@staticmethod
	@make_safe
	def from_dictionary(safe_dictionary):
		keys = StudentName.keys
		if not (keys[0] in safe_dictionary and keys[1] in safe_dictionary):
			logging.debug('About to fail at dictionary {}'.format(safe_dictionary))
			raise KeyError('No name could be extracted from the dictionary {}'.format(safe_dictionary))

		preferred_name = None

		if keys[2] in safe_dictionary:
			preferred_name = safe_dictionary[keys[2]]

		name = StudentName(
			first = safe_dictionary[keys[0]],
			last = safe_dictionary[keys[1]],
			preferred = preferred_name
		)
		if name is None:
			print(name)
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
	The keys required from a dictionary. Also used to export to csv. Not case sensitive
	'''
	keys = ['Student ID', 'Email', 'Major']

	@make_safe
	def __init__(self, safe_dictionary):
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
		self._name = StudentName.from_dictionary(safe_dictionary)
		self._status = StudentStatus.from_dictionary(safe_dictionary)
		self._year = StudentYear.from_dictionary(safe_dictionary)

		for key in Student.keys:
			if key in safe_dictionary:
				safe_key = SafeDictionary.make_key_safe(key)
				attribute_name = '_{}'.format(safe_key)
				setattr(self, attribute_name, safe_dictionary[key])
			else:
				raise KeyError('Student dictionary missing {}. Must have list {}, got list {}'.format(
					key,
					Student.keys,
					list(safe_dictionary)
				))
	
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
		if not isinstance(status, StudentStatus):
			raise ValueError('Status must be an instance of the enum StudentStatus')
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
			safe_key = SafeDictionary.make_key_safe(key)
			data[key] = getattr(self, safe_key)
		self.status.to_dictionary(data)
		self.year.to_dictionary(data)
		self.name.to_dictionary(data)

		return data

	def __str__(self):
		return self.name.expanded
	
	def __repr__(self):
		return 'Student({})'.format(str(self))
