'''
A class representing the student information stored on HokieSpa.
'''


class HokieSpaStudent(object):
	def __init__(self, id_number=None, first_name=None, last_name=None, grade=None, grade_option=None, major=None, year=None, email=None, confidential=None, phone=None):
		self._id_number = id_number
		self._first_name = first_name
		self._last_name = last_name
		self._grade = grade
		self._grade_option = grade_option
		self._major = major
		self._year = year
		self._email = email
		self._confidential = confidential
		self._phone = phone
	
	@property
	def id_number(self):
		return self._id_number
	@property
	def first_name(self):
		return self._first_name
	
	@property
	def last_name(self):
		return self._last_name
	
	@property
	def grade(self):
		return self._grade
	
	@property
	def grade_option(self):
		return self._grade_option
	
	@property
	def major(self):
		return self._major
	
	@property
	def year(self):
		return self._year
	
	@property
	def email(self):
		return self._email
	
	@property
	def confidential(self):
		return self._confidential
	
	@property
	def phone(self):
		return self._phone
