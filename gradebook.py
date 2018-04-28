import configparser
import csv_io
import config
import logging
import os

from student import *

def average(numbers, scale=1.0):
	return sum(numbers) / (1.0*len(numbers)) / (1.0*scale)

def weighted_average(numbers, weights):
	return sum(n*w for n,w in zip(numbers, weights)) / (1.0*sum(weights))

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
	
	def __iter__(self):
		for key in sorted(self._categories.keys()):
			yield self._categories[key]
	
	def __getitem__(self, key):
		return self._categories[key]

	@property
	def weight(self):
		return sum(c.weight for c in self)
	
	def student_by_id(self, id_val):
		for student in self._students:
			if student.student_id == id_val:
				return student
	
	def single_average(self, student):
		numbers = [c.single_average(student) for c in self]
		weights = [c.weight for c in self]
		return weighted_average(numbers, weights)
	
	def average(self):
		return average([self.single_average(s) for s in self._students])
	

class GradeCategory(object):
	def __init__(self, directory, students):
		self._assignments = dict()
		basepath = os.path.join(config.GRADES_DIR, directory)
		self._load_weights(basepath)
		self._name = directory
		
		for assignment_file in os.listdir(basepath):
			name, ext = os.path.splitext(assignment_file)
			assignment_path = os.path.join(basepath, assignment_file)
			if os.path.isfile(assignment_path) and ext == '.csv':
				self._add_assignment(
					Assignment(
						name,
						students,
						self._weights.get_points(name),
						filepath=assignment_path
					)
				)

	def _load_weights(self, directory):
		filepath = os.path.join(directory, 'weights.ini')
		self._weights = CategoryWeightsFactory.from_file(filepath)
	
	def _add_assignment(self, assignment):
		self._assignments[assignment.name] = assignment
	
	def __iter__(self):
		for key in sorted(self._assignments.keys()):
			yield self._assignments[key]
	
	def __getitem__(self, assignment):
		return self._assignments[assignment]

	@property
	def name(self):
		return self._name
	
	@property
	def weight(self):
		return self._weights.weight
	
	def average(self):
		'''
		The average over all students. Taken by the average over its
		assignments.
		'''
		assignments = [a.average() for a in self]
		return average(assignments)

	def single_average(self, student):
		assignments = [a.get_percentage(student) for a in self]
		return average(assignments)


class WebAssignCategory(GradeCategory):
	def __init__(self, students): # Note, doesn't call super constructor
		self._assignments = dict()
		self._load_assignments(students)
		self._name = 'WebAssign'
	
	def _load_assignments(self, students):
		ordered_assignments, ordered_points, scores = self._dissect_wa_file()
		username_map = self._parse_username_map(scores, students)
		self._weights = CategoryWeightsFactory.for_webassign(ordered_assignments, ordered_points)

		for name, assignment_map in self._iterate_assignment_maps(username_map, ordered_assignments, scores):
			self._add_assignment(Assignment(
				name,
				students,
				self._weights.get_points(name),
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


class Assignment(object):
	def __init__(self, name, students, points, filepath=None, assignment_map=None):
		self._name = name
		self._points = points
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
	
	@staticmethod
	def text_to_score(data):
		try:
			return float(data)
		except ValueError:
			return 0.0
	
	@property
	def name(self):
		return self._name
	
	def by_id(self, student_id):
		for student in self._grades:
			if student_id == student.student_id:
				return Assignment.text_to_score(self._grades[student])
		else:
			raise KeyError('Student id {} not found in assignment {}'.format(
				student_id,
				self.name
			))
	
	def average(self):
		grades = [self[s] for s in self._grades]
		return average(grades, scale=self._points)

	def __hash__(self):
		return hash(self.name)
	
	def __getitem__(self, student):
		return self.by_id(student.student_id)

	def get_percentage(self, student):
		return self[student] / self._points


class CategoryWeights(object):
	def __init__(self, category_weight, point_map=None, equal_points=None):
		self._weight = category_weight
		self._point_map = point_map
		self._equal_points = equal_points

	def get_points(self, assignment):
		'''
		Given the provided configuration, attempt to parse what the maximal
		points for this Assignment should be.
		'''
		key = assignment.lower()

		if self._equal_points is None:
			if key not in self._point_map:
				logging.debug(self._point_map)
				print(self._point_map)
				raise Exception('Assignment "{}" does not have a weight in its category.'.format(assignment))
			else:
				return self._point_map[key]
		else:
			return self._equal_points
	
	@property
	def weight(self):
		return self._weight


class CategoryWeightsFactory(object):
	@staticmethod
	def from_file(filepath):
		'''
		Take an ini file that describes the weights for the category and the
		assignments within.
		'''
		section = 'Meta'
		parser = configparser.ConfigParser()
		parser.read(filepath)
		data = dict()

		if section not in parser:
			print(parser.sections())
			raise Exception('Weight config {} did not contain a "Meta" section.'.format(filepath))

		for key in parser[section]:
			data[key] = parser.getfloat(section, key)

		return CategoryWeightsFactory.from_factory_data(data)

	@staticmethod
	def for_webassign(ordered_assignments, ordered_points):
		grade_config = config.load_configuration_from_file(config.GRADING_PATH)
		category_weight = grade_config['General'].getfloat('WebAssignWeight')
		data = {'weight': category_weight}

		for assignment, points in zip(ordered_assignments, ordered_points):
			data[assignment.lower()] = float(points)

		return CategoryWeightsFactory.from_factory_data(data)

	@staticmethod
	def from_factory_data(data):
		category_weight = CategoryWeightsFactory.parse_category_weight(data)
		equal_points = CategoryWeightsFactory.parse_equal_points(data)
		point_map = CategoryWeightsFactory.parse_point_map(data)

		return CategoryWeights(
			category_weight,
			point_map=point_map,
			equal_points=equal_points
		)

	@staticmethod
	def parse_category_weight(data):
		'''
		Enforce there is a category weight, return the weight, and remove the
		data from the dictionary.
		'''
		key = 'weight'
		if key not in data:
			raise KeyError('Category weight not specified in Meta section of {}'.format(filepath))
		
		weight = data[key]
		del data[key]

		return weight
		
	@staticmethod
	def parse_equal_points(data):
		'''
		Attempts to find the equal_weights keys, and if present return it. 
		Otherwise return None. In either case, remove the key.
		'''
		key = 'equal points'
		equal_points = None

		if key in data:
			equal_points = data[key]
			del data[key]

		return equal_points

	def parse_point_map(data):
		point_map = dict()

		reserved_keys = ['equal_points', 'weight']
		for key in data:
			if key not in reserved_keys:
				point_map[key] = data[key]

		if len(point_map) == 0:
			point_map = None

		return point_map


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

