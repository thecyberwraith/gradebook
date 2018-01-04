from unittest import TestCase
from student import *

class TestStudentName(TestCase):
	def test_constructor_without_preferred_name(self):
		name = StudentName('bob', 'joe')
		self.assertEqual('bob', name.first)
		self.assertEqual('joe', name.last)
		self.assertEqual(None, name._preferred)
	
	def test_constructor_with_preferred_name(self):
		name = StudentName('bob', 'joe', 'susie')
		self.assertEqual('bob', name.first)
		self.assertEqual('joe', name.last)
		self.assertEqual('susie', name._preferred)
	
	def test_property_first_last(self):
		name = StudentName('bob', 'joe', 'susie')
		self.assertEqual('bob joe', name.first_last)

	def test_property_last_first(self):
		name = StudentName('bob', 'joe')
		self.assertEqual('joe, bob', name.last_first)

	def test_property_preferred_without_preferred(self):
		name = StudentName('bob', 'joe')
		self.assertEqual('bob joe', name.preferred)
	
	def test_property_preferred_with_preferred(self):
		name = StudentName('bob', 'joe', 'susie')
		self.assertEqual('susie joe', name.preferred)
	
	def test_property_expanded_without_preferred(self):
		name = StudentName('bob', 'joe')
		self.assertEqual('bob joe', name.expanded)
	
	def test_property_expanded_with_preferred(self):
		name = StudentName('bob', 'joe', 'susie')
		self.assertEqual('bob (susie) joe', name.expanded)
	
	def test_staticmethod_from_dictionary(self):
		name_components = ['bob', 'joe', 'susie']
		dictionary = {StudentName.keys[i]: name_components[i] for i in range(3)}
		name = StudentName.from_dictionary(dictionary)
		self.assertEqual('bob', name.first)
		self.assertEqual('joe', name.last)
		self.assertEqual('susie', name._preferred)

	def test_method_to_dictionary(self):
		name_components = ['bob', 'joe', 'susie']
		name_dict = {StudentName.keys[i]: name_components[i] for i in range(3)}
		name = StudentName.from_dictionary(name_dict)
		result = dict()
		name.to_dictionary(result)
		self.assertEqual(name_dict, result)

class TestStoredEnums(TestCase):
	def test_from_dictionary_status(self):
		self.assertEqual(
			StudentStatus.ACTIVE,
			StudentStatus.from_dictionary({StudentStatus.get_key(): 'Active'})
		)
	
	def test_to_dictionary(self):
		result = dict()
		StudentStatus.DROPPED.to_dictionary(result)
		self.assertEqual(result, {StudentStatus.get_key(): 'DROPPED'})
	
	def test_error_on_save_undefined(self):
		with self.assertRaises(ValueError):
			StudentStatus.UNDEFINED.to_dictionary(dict())
		with self.assertRaises(ValueError):
			StudentYear.UNDEFINED.to_dictionary(dict())

class TestStudent(TestCase):
	def setUp(self):
		self.sample_data = {
			'Student id': 5,
			'First name': 'bob',
			'Last name': 'joe',
			'Preferred': 'susie',
			'Email': 'bjoe@com.net',
			'Year': 'Sophomore',
			'Major': 'Ice Cream Technician',
			'Status': 'Active',
		}

	def test_constructor(self):
		Student(self.sample_data)
	
	def test_constructor_fails_with_insufficient_data(self):
		data = self.sample_data.copy()
		del data['Student id']
		with self.assertRaises(KeyError):
			Student(data)
	
	def test_constructor_fails_with_bad_year(self):
		data = self.sample_data.copy()
		data['Year'] = 'old'
		with self.assertRaises(KeyError):
			Student(data)
	
	def test_constructor_fails_with_bad_status(self):
		data = self.sample_data.copy()
		data['Status'] = 'Homeschooled'
		with self.assertRaises(KeyError):
			Student(data)
	
	def test_set_values(self):
		student = Student(self.sample_data)
		self.assertEqual(student.student_id, self.sample_data['Student id'])
		self.assertEqual(student.email, self.sample_data['Email'])
		self.assertEqual(student.major, self.sample_data['Major'])
		self.assertEqual(student.year, StudentYear.SOPHOMORE)
		self.assertEqual(student.status, StudentStatus.ACTIVE)
	
	def test_pid(self):
		student = Student(self.sample_data)
		self.assertEqual(student.pid, 'bjoe')
	
	def test_to_dictionary(self):
		student = Student(self.sample_data)
		result = student.to_dictionary()
	
	def test_setter_status(self):
		student = Student(self.sample_data)
		self.assertEqual(student.status, StudentStatus.ACTIVE)
	
	def test_setter_status_type(self):
		student = Student(self.sample_data)
		with self.assertRaises(ValueError):
			student.status = 'WITHDRAWN'
		student.status = StudentStatus.WITHDRAWN
