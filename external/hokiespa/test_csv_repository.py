from unittest import TestCase
from tempfile import TemporaryDirectory
from os.path import join as path_join

from gradebook.external.hokiespa.csv_repository import HokieSpaCSVRepository
from gradebook.external.hokiespa.student import HokieSpaStudent


class TestHokieSpaCSVRepositoryConstructor(TestCase):
	def setUp(self):
		self.tmpdir = TemporaryDirectory()
	
	def tearDown(self):
		self.tmpdir.cleanup()

	def test_correct_construction(self):
		import_path = path_join(self.tmpdir.name, 'import.csv')
		export_path = path_join(self.tmpdir.name, 'export.csv')

		with open(import_path, 'w'):
			pass

		HokieSpaCSVRepository(import_path, export_path)
	
	def test_failure_if_import_does_not_exist(self):
		import_path = path_join(self.tmpdir.name, 'import.csv')
		export_path = path_join(self.tmpdir.name, 'export.csv')

		with self.assertRaises(FileNotFoundError):
			HokieSpaCSVRepository(import_path, export_path)
	
	def test_failure_if_export_dir_does_not_exist(self):
		import_path = path_join(self.tmpdir.name, 'import.csv')
		export_path = path_join(self.tmpdir.name, 'NotExists', 'export.csv')

		with open(import_path, 'w'):
			pass

		with self.assertRaises(FileNotFoundError):
			HokieSpaCSVRepository(import_path, export_path)

class TestHokieSpaCSVRepositoryTransfers(TestCase):
	def setUp(self):
		self.tmpdir = TemporaryDirectory()
		self.import_path = path_join(self.tmpdir.name, 'import.csv')
		self.export_path = path_join(self.tmpdir.name, 'export.csv')
		self.set_import_data([])
		self.repo = HokieSpaCSVRepository(self.import_path, self.export_path)
	
	def tearDown(self):
		self.tmpdir.cleanup()
	
	def set_import_data(self, rows):
		with open(self.import_path, 'w') as f:
			for row in rows:
				print(row, file=f)
	
	def test_import_of_empty_data(self):
		result = self.repo.import_hokiespa_roster()

		self.assertEqual(0, len(result))
	
	def test_import_of_students(self):
		self.set_import_data([
			'0,1,2,3,4,5,6,7,8,9',
			'a,b,c,d,e,f,g,h,i,j',
		])

		result = self.repo.import_hokiespa_roster()

		self.assertEqual(2, len(result))
		self.assertEqual('2', result[0].last_name)
	
	def test_export_of_students(self):
		student = HokieSpaStudent(0,1,2,3,4,5,6,7,8)
		self.repo.export_hokiespa_gradesheet([student])
		with open(self.export_path, 'r') as f:
			lines = f.readlines()
			self.assertEqual(
				','.join(HokieSpaCSVRepository.CSV_HEADERS),
				lines[0].strip()
			)
			self.assertEqual(
				'0,1,2,3,4,5,6,7,8,',
				lines[1].strip()
			)
