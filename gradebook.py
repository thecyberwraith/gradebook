import configparser
import csv_io
import config
import logging
import os

from student import *


class Gradebook(object):
	def __init__(self):
		self._categories = dict()
		self._students = get_active_students()
		self._load_categories()
	
	def _load_categories(self):
		self._add_category(WebAssignCategory(self._students))
		for category_name in os.listdir(config.GRADES_DIR):
			category_directory = os.path.join(config.GRADES_DIR, category_name)
			if os.path.isdir(category_directory):
				self._add_category(GradeCategory(
					category_name,
					self._students
				))
	
	def _add_category(self, category):
		self._categories[category.name] = category
	
	@property
	def weight(self):
		return sum(c.weight for c in self)
	
	def __iter__(self):
		for key in sorted(self._categories.keys()):
			yield self._categories[key]
	
	def __getitem__(self, key):
		return self._categories[key]


class GradeCategory(object):
	def __init__(self, directory, students):
		self._assignments = dict()
		basepath = os.path.join(config.GRADES_DIR, directory)
		self._load_metadata(basepath)
		self._name = directory
		
		for assignment_file in os.listdir(basepath):
			name, ext = os.path.splitext(assignment_file)
			assignment_path = os.path.join(basepath, assignment_file)
			if os.path.isfile(assignment_path) and ext == '.csv':
				self._add_assignment(
					Assignment(
						name,
						students,
						filepath=assignment_path
					)
				)

	def _load_metadata(self, directory):
		filepath = os.path.join(directory, 'meta.ini')
		self._metadata = CategoryMetadata(filepath=filepath)
	
	def _add_assignment(self, assignment):
		self._assignments[assignment.name] = assignment
	
	@property
	def name(self):
		return self._name
	
	@property
	def weight(self):
		return self._metadata.weight

	def __iter__(self):
		for key in sorted(self._assignments.keys()):
			yield self._assignments[key]


class WebAssignCategory(GradeCategory):
	def __init__(self, students): # Note, doesn't call super constructor
		self._assignments = dict()
		self._load_assignments(students)
		self._name = 'WebAssign'
	
	def _load_assignments(self, students):
		ordered_assignments, ordered_points, scores = self._dissect_wa_file()
		username_map = self._parse_username_map(scores, students)

		self._set_metadata(ordered_assignments, ordered_points)

		for name, assignment_map in self._iterate_assignment_maps(username_map, ordered_assignments, scores):
			self._add_assignment(Assignment(
				name,
				students,
				assignment_map=assignment_map
			))

	def _dissect_wa_file(self):
		logging.debug('Parsing WebAssign file')
		
		# Get the CSV file
		wa_contents = csv_io.load_rows(config.INPUT_WA_SCORES_PATH)
		
		# The first 4 (0-3) rows are information about the class and download date
		# The next row (4) contains assignment names from column 5 onward (zero index)
		# Similarly, row 5 contains the point values for those same assignments
		# A blank row for readability?
		# Finally, the student table. First row here outlines the headers
		# [Fullname, Username, Student ID]
		# before finally getting down to the scores...

		ordered_assignments = wa_contents[4][5:] # Keep the order for the names
		ordered_points = wa_contents[5][5:] # Keep the order for the points
		scores = wa_contents[9:]
		return ordered_assignments, ordered_points, scores

	def _parse_username_map(self, scores, students):
		'''
		Try to match the students WebAssign username to an actual student id,
		since the WebAssign student id is worthless (thanks FERPA?).
		Apparently, the WA username is a prefix for the email (aka PID)
		'''
		username_to_id = {}
		for row in scores:
			wa_username = row[1]
			for student in students:
				if student.email.startswith(wa_username):
					username_to_id[wa_username] = student.student_id
					break
			
			if wa_username not in username_to_id:
				print('\tUnable to find match for WebAssign id "{}" in roster emails.'.format(wa_username))
		
		return username_to_id
	
	def _iterate_assignment_maps(self, username_to_id_map, ordered_assignments, scores):
		# Scores start after 4 columns of identifying info
		score_offset = 5

		for assignment_index, assignment_name in enumerate(ordered_assignments):
			grade_map = dict()
			for student_scores in scores:
				email = student_scores[1]
				if email not in username_to_id_map:
					continue
				student_score = student_scores[score_offset + assignment_index]
				student_score = self._parse_score(student_score)
				grade_map[username_to_id_map[email]] = student_score

			yield assignment_name, grade_map

	def _parse_score(self, score):
		try:
			return float(score)
		except ValueError:
			return 0

	def _set_metadata(self, ordered_assignments, ordered_points):
		grade_config = config.load_configuration_from_file(config.GRADING_PATH)
		category_weight = grade_config['General'].getfloat('WebAssignWeight')
		weight_map = {assignment: points for assignment, points in zip(ordered_assignments, ordered_points)}
		self._metadata = CategoryWeights(category_weight, weight_map=weight_map)


class Assignment(object):
	def __init__(self, name, students, filepath=None, assignment_map=None):
		self._name = name
		self._grades = dict()
		if filepath:
			assignment_map = self._get_assignment_map_from_file(filepath)
		self._load_from_assignment_map(students, assignment_map)
	
	def _get_assignment_map_from_file(self, filepath):
		dicts = csv_io.read_dataset(filepath)
		assignment_map = dict()
		for datum in dicts:
			assignment_map[datum['Student ID']] = datum['Score']
		return assignment_map
	
	def _load_from_assignment_map(self, students, assignment_map):
		for student in students:
			for student_id in assignment_map:
				if student.student_id == student_id:
					self._grades[student] = assignment_map[student_id]
					break
			else:
				raise KeyError('{!r} does not have a grade in {.name}'.format(student, self))
	
	@property
	def name(self):
		return self._name
	
	def __hash__(self):
		return hash(self.name)


class CategoryWeights(object):
	def __init__(self, category_weight, weight_map=None, equal_weight=None):
		self.weight = category_weight
		self.weight_map = weight_map
		self.equal_weight = equal_weight


class CategoryMetadata(object):
	def __init__(self, filepath=None, data=None):
		'''
		data would be a dictionary like a metadata config file.
		'''
		if data is None:
			data = self._get_data_from_file(filepath)

		self._data = data
	
	def _get_data_from_file(self, filepath):
		parser = configparser.ConfigParser()
		parser.read(filepath)
		data = dict()
		for key in parser['Meta']:
			data[key] = parser.getfloat('Meta', key)
		if 'weight' not in data:
			raise KeyError('Weight not specified in Metadata {}'.format(filepath))
		return data
	
	@property
	def weight(self):
		return self._data['weight']

def get_all_students():
	'''
	Get all students regardless of status.
	'''
	return [Student(s) for s in csv_io.read_dataset(config.ROSTER_PATH)]

def get_active_students():
	'''
	Load all students from the roster whose status is active.
	If there are no students, return None.
	'''
	students = get_all_students()
	students = [s for s in students if s.status == StudentStatus.ACTIVE]

	return students

