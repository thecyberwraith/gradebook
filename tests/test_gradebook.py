from tests.setup import ConfiguredWithWebAssign, ConfiguredWithGrades

from gradebook import *
from student import StudentStatus
from update_roster import write_to_file

class TestStudentsGetter(ConfiguredWithWebAssign):
	def test_get_all_students(self):
		students = get_all_students()
		self.assertEqual(len(students), len(self.sample_data))
	
	def test_get_active_students_on_drop(self):
		students = get_all_students()
		students[0].status = StudentStatus.DROPPED
		write_to_file(students)
		self.assertEqual(len(get_all_students())-1, len(get_active_students()))

	def test_get_active_students_on_withdraw(self):
		students = get_all_students()
		students[0].status = StudentStatus.WITHDRAWN
		write_to_file(students)
		self.assertEqual(len(get_all_students())-1, len(get_active_students()))


class TestWebAssignCategory(ConfiguredWithWebAssign):
	def test_constructor(self):
		students = get_active_students()
		category = WebAssignCategory(students)


class TestGradebook(ConfiguredWithGrades):
	def test_constructor(self):
		Gradebook()
	
	def test_categories(self):
		gradebook = Gradebook()
		sections = {'Homework', 'Tests', 'WebAssign'}
		values = {category.name for category in gradebook}
		self.assertEqual(sections, values)
	
	def test_wa_assignments(self):
		gradebook = Gradebook()
		assignments = {'WA 1', 'WA 2', 'WA 3'}
		values = {assignment.name for assignment in gradebook['WebAssign']}
		self.assertEqual(assignments, values)

	def test_homework_assignments(self):
		gradebook = Gradebook()
		assignments = {'Homework 1', 'Homework 2', 'Homework 3'}
		values = {assignment.name for assignment in gradebook['Homework']}
		self.assertEqual(assignments, values)

	def test_tests_assignments(self):
		gradebook = Gradebook()
		assignments = {'Test 1', 'Test 2'}
		values = {assignment.name for assignment in gradebook['Tests']}
		self.assertEqual(assignments, values)
	
	def test_weight(self):
		gradebook = Gradebook()
		self.assertEqual(gradebook.weight, 0.8)
