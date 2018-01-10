import pdb
from interact import *
from student import Student

from tests.setup import InputControllingSetup


class TestInteractiveFindStudent(InputControllingSetup):
	def setUp(self):
		super(TestInteractiveFindStudent, self).setUp()
		shared_data = {
			'Student Id': 1,
			'Email': 'trash@trsh.com',
			'Preferred': '',
			'Year': 'Freshman',
			'Status': 'Active',
			'Major': 'Useless',
		}

		student_data = [{
				'First Name': 'Bob',
				'Last Name': 'Joe',
			},
			{
				'First Name': 'Susie',
				'Last Name': 'Joe',
			},
			{
				'First Name': 'Joe',
				'Last Name': 'Joes',
			},
			{
				'First Name': 'Adam',
				'Last Name': 'Chetly',
			},

		]

		self.students = []
		for data in student_data:
			data.update(shared_data)
			self.students.append(Student(data))

	def tearDown(self):
		super(TestInteractiveFindStudent, self).tearDown()

	def test_all_pass_new_filter(self):
		new_filter = NameFilter()
		filtered = new_filter.filter_candidates(self.students)
		self.assertEqual(len(filtered), len(self.students))
	
	def test_early_find(self):
		new_filter = NameFilter(last='C')
		filtered = new_filter.filter_candidates(self.students)
		self.assertEqual(len(filtered), 1)
	
	def test_filter_to_multiples(self):
		new_filter = NameFilter(last='joe')
		filtered = new_filter.filter_candidates(self.students)
		self.assertEqual(len(filtered), 3)
	
	def test_last_name_exact_filter(self):
		new_filter = NameFilter(last='joe ')
		filtered = new_filter.filter_candidates(self.students)
		self.assertEqual(len(filtered), 2)
	
	def test_last_and_first_filter(self):
		new_filter = NameFilter(last='joe ', first='s')
		filtered = new_filter.filter_candidates(self.students)
		self.assertEqual(len(filtered), 1)
	
	def test_none_found(self):
		new_filter = NameFilter(last='pat')
		filtered = new_filter.filter_candidates(self.students)
		self.assertEqual(len(filtered), 0)
	
	def test_auto_complete(self):
		new_filter = NameFilter('j')
		filtered = new_filter.filter_candidates(self.students)
		self.assertEqual(len(filtered), 3)
		new_filter.auto_complete(filtered)
		self.assertEqual(new_filter._last, 'joe')
	
	def test_sequenced_interactive_filter(self):
		self.set_input(['j', ' ', 's'])
		new_filter = NameFilter()
		students = self.students
		self.assertEqual(len(students), 4)
		new_filter.update_filter(students)
		students = new_filter.filter_candidates(students)
		self.assertEqual(len(students), 3)
		new_filter.auto_complete(students)
		new_filter.update_filter(students)
		students = new_filter.filter_candidates(students)
		self.assertEqual(len(students), 2)
		new_filter.update_filter(students)
		students = new_filter.filter_candidates(students)
		self.assertEqual(len(students), 1)
	
	def test_full_interactive_method(self):
		self.set_input(['j', ' ', 's'])
		student = interactive_find_student(self.students)
		self.assertIsNotNone(student)
		self.assertEqual(student.name.first, 'Susie')
