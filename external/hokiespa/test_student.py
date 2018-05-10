from unittest import TestCase

from gradebook.external.hokiespa.student import HokieSpaStudent


class TestStudent(TestCase):
	FIELDS = ['id_number', 'first_name', 'last_name', 'grade', 'grade_option', 'major', 'year', 'email', 'confidential', 'phone']

	def test_constructor_getters(self):
		for field in TestStudent.FIELDS:
			value = 'Tester'+field
			data = {field: value}
			s = HokieSpaStudent(**data)
			self.assertEqual(
				getattr(s, field),
				value,
				'Failed to get field {} after set in the constructor.'
			)
	
	def test_only_settable(self):
		s = HokieSpaStudent()
		for field in TestStudent.FIELDS:
			with self.assertRaises(AttributeError):
				setattr(s, field, None)
