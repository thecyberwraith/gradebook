import unittest

import student

class TestStudentName(unittest.TestCase):
	def test_constructor_without_preferred_name(self):
		name = student.StudentName('bob', 'joe')
		self.assertEqual('bob', name.first)
		self.assertEqual('joe', name.last)
		self.assertEqual(None, name._preferred)
	
	def test_constructor_with_preferred_name(self):
		name = student.StudentName('bob', 'joe', 'susie')
		self.assertEqual('bob', name.first)
		self.assertEqual('joe', name.last)
		self.assertEqual('susie', name._preferred)
	
	def test_property_first_last(self):
		name = student.StudentName('bob', 'joe', 'susie')
		self.assertEqual('bob joe', name.first_last)

	def test_property_last_first(self):
		name = student.StudentName('bob', 'joe')
		self.assertEqual('joe, bob', name.last_first)

	def test_property_preferred_without_preferred(self):
		name = student.StudentName('bob', 'joe')
		self.assertEqual('bob joe', name.preferred)
	
	def test_property_preferred_with_preferred(self):
		name = student.StudentName('bob', 'joe', 'susie')
		self.assertEqual('susie joe', name.preferred)
	
	def test_property_expanded_without_preferred(self):
		name = student.StudentName('bob', 'joe')
		self.assertEqual('bob joe', name.expanded)
	
	def test_property_expanded_with_preferred(self):
		name = student.StudentName('bob', 'joe', 'susie')
		self.assertEqual('bob (susie) joe', name.expanded)
	
	def test_staticmethod_from_dictionary(self):
		name_components = ['bob', 'joe', 'susie']
		dictionary = {student.StudentName.keys[i]: name_components[i] for i in range(3)}
		name = student.StudentName.from_dictionary(dictionary)
		self.assertEqual('bob', name.first)
		self.assertEqual('joe', name.last)
		self.assertEqual('susie', name._preferred)
