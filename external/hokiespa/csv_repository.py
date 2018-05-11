from gradebook.external.hokiespa.repository import HokieSpaRepository
from gradebook.external.hokiespa.student import HokieSpaStudent
from gradebook.io.csv import read_dict_from_source, write_dict
from os.path import dirname, isfile, isdir


class HokieSpaCSVRepository(HokieSpaRepository):
	'''
	This class retrieves and stores hokiespa rosters to and from CSV files that
	are specified in the constructors.
	'''
	CSV_HEADERS = [
		'id_number',
		'first_name',
		'last_name',
		'grade',
		'grade_option',
		'major',
		'year',
		'email',
		'confidential',
		'phone',
	]

	def __init__(self, import_filename, export_filename):
		if not isfile(import_filename):
			raise FileNotFoundError(
				'There is no HokieSpa file at {}'.format(
					import_filename
				)
			)
		if not isdir(dirname(export_filename)):
			raise FileNotFoundError(
				'There is no directory to save the HokieSpa file for {}'.format(
					export_filename
				)
			)

		self._import_filename = import_filename
		self._export_filename = export_filename

	def import_hokiespa_roster(self):
		with open(self._import_filename, 'r') as import_file:
			students = read_dict_from_source(
				import_file,
				headers=HokieSpaCSVRepository.CSV_HEADERS,
			)
			return [HokieSpaStudent(**dictionary) for dictionary in students]

	def export_hokiespa_gradesheet(self, students):
		data_rows = []
		for student in students:
			new_data = dict()
			for field in HokieSpaCSVRepository.CSV_HEADERS:
				new_data[field] = getattr(student, field)
			data_rows.append(new_data)

		with open(self._export_filename, 'w') as export_file:
			write_dict(
				export_file,
				HokieSpaCSVRepository.CSV_HEADERS,
				data_rows,
			)
