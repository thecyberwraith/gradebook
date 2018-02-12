import csv
import config
import os

class Student(object):
	'''
	Takes a dictionary of information and puts it all into an object that
	easily manages the data.
	'''

	'''
	The keys required from a dictionary. Also used to export to csv.
	'''
	keys = ['Student ID', 'First Name', 'Last Name', 'Email', 'Preferred Name', 'Year', 'Status', 'Major']

	def __init__(self, data):
		'''
		Given a dictionary of data, create a student with the specified
		information. This data should contain the following keys:
			
			First Name
			Last Name
			Student ID
			Email
			Preferred Name
			Year
			Status
			Major
		'''

		for key in Student.keys:
			safe_key = '_{}'.format(key.replace(' ', '_').lower())
			setattr(self, safe_key, data[key])
	
	@property
	def first_name(self):
		return self._first_name
	
	@property
	def last_name(self):
		return self._last_name
	
	@property
	def preferred_name(self):
		return self._preferred_name

	@property
	def student_id(self):
		return self._student_id
	
	@property
	def email(self):
		return self._email
	
	@property
	def year(self):
		return self._year
	
	@property
	def status(self):
		return self._status
	
	@status.setter
	def status(self, status):
		self._status = status
	
	@property
	def major(self):
		return self._major

	@property
	def name(self):
		'''
		Get the student's preferred first name last name string.
		'''
		result = ''
		if self.preferred_name:
			result = self.preferred_name
		else:
			result = self.first_name

		return result + ' ' + self.last_name
	
	@property
	def last_first_name(self):
		return '{}, {}'.format(self.last_name, self.first_name)
	
	@property
	def pid(self):
		'''
		Given a student dictionary, take the email for the students and grab
		the PID portion.
		'''
		email = self.email
		return email[:email.find('@')]
	
	def to_dictionary(self):
		'''
		Return a dictionary with keys from Student.keys.
		'''
		data = dict()
		for key in Student.keys:
			data[key] = getattr(self, '_{}'.format(key.replace(' ', '_')).lower())

		return data

	def __str__(self):
		return self.name

def get_categorized_gradebook():
	'''
	Given a file with WebAssign grades, create a gradebook with categories
	using the locally stored grades.
	'''
	students = get_active_students()
	wa_grades = parse_webassign(students)
	local_grades = parse_local_grades()
	full_gradebook = local_grades.copy()
	full_gradebook['WebAssign'] = wa_grades

	return full_gradebook

def parse_webassign(students):
	'''
	WebAssign sends out a mostly human readable, but terriblely formatted
	gradesheet. Tread the notes carefully.

	returns - a dictionary gradebook. The keys are the quiz names. The data for
	a quiz is another dictionary, this one containing student ids that map to
	the points for that student. NS or ND are interpreted as 0.
	'''
	print('Parsing WebAssign file')
	
	# Get the TAB sepearated CSV file
	wa_contents = []
	with open(config.INPUT_WA_SCORES_PATH, 'r') as wa_file:
		reader = csv.reader(wa_file)
		for row in reader:
			wa_contents.append(row)
	
	# The first 4 (0-3) rows are information about the class and download date
	# The next row (4) contains assignment names from column 5 onward (zero index)
	# Similarly, row 5 contains the point values for those same assignments
	# A blank row for readability?
	# Finally, the student table. First row here outlines the headers
	# [Fullname, Username, Student ID]
	# before finally getting down to the scores...

	ordered_assignments = wa_contents[4][5:] # Keep the order for the scores
	assignments = {assignment: dict() for assignment in ordered_assignments}
	scores = wa_contents[9:]

	# Next, try to match the students WebAssign username to an actual student
	# id, since the WebAssign student id is worthless (thanks FERPA?).
	# Apparently, the WA username is a prefix for the email (aka PID)
	username_to_id = {}
	for row in scores:
		wa_username = row[1]
		prefix = wa_username[:wa_username.find('@')]
		for student in students:
			if student.email.startswith(prefix):
				username_to_id[wa_username] = student.student_id
				break
		
		if wa_username not in username_to_id:
			print('\tUnable to find match for WebAssign id "{}" in roster emails.'.format(wa_username))
	
	# For my next trick, I iterate through the scores and assign everything
	# into the assignments dictionary.
	for row in scores:
		if row[1] not in username_to_id:
			continue

		student_id = username_to_id[row[1]]

		for assignment, score in zip(ordered_assignments, row[5:]):
			try:
				score=float(score)
			except ValueError:
				score=0

			assignments[assignment][student_id] = score
	
	# For my final trick, I assign the max points for each assignment. When I
	# created this, the max was uniform to 20.
	# TODO Update to properly read the max points.
	for assignment in assignments:
		assignments[assignment]['points'] = 20

	return assignments

def parse_local_grades():
	'''
	Explore the grades folder. Each subfolder is an assignment group. Each file
	in each subfolder is a single graded item. Then each graded item is a score
	dictionary.
	'''
	local_grades = dict()

	for group in os.listdir(config.GRADES_DIR):
		if os.path.isdir(os.path.join(config.GRADES_DIR, group)):
			local_grades[group] = parse_grouped_grades(group)
	
	return local_grades 

def parse_grouped_grades(group):
	'''
	Explore each subfile in the group folder, and load them into a gradebook.
	'''
	assignments = dict()
	print('Looking up group {}'.format(group))
	basepath = os.path.join(config.GRADES_DIR, group)

	for assignment in os.listdir(basepath):
		name, ext = os.path.splitext(assignment)
		if os.path.isfile(os.path.join(basepath, assignment)) and ext == '.csv':
			assignments[name] = parse_assignment(os.path.join(basepath, assignment))

		# Assign the max points based on the groups
		if group == 'homework':
			assignments[name]['points'] = 10
	
	return assignments 

def parse_assignment(filepath):
	'''
	Return a dictionary mapping student ids to grades for a given assignment.
	'''
	print('\tParsing assignment {}'.format(filepath))
	scores = dict()

	with open(filepath, 'r') as f:
		reader = csv.DictReader(f)
		for row in reader:
			scores[row['Student ID']] = row['Score']
	
	return scores

def get_all_students():
	'''
	Get all students regardless of status.
	'''
	students = None
	with open(config.ROSTER_PATH, 'r') as f:
		reader = csv.DictReader(f)
		
		students = [Student(s) for s in reader]
	
	return students

def get_active_students():
	'''
	Load all students from the roster whose status is active.
	If there are no students, return None.
	'''
	students = get_all_students()
	students = [s for s in students if s.status == 'Active']

	return students

def interactive_find_student():
	'''
	Check the list of students by first checking the last name, then
	first name until a unique student is found. If a Keyboard Interrupt
	is thrown, then None is returned.
	'''
	students = get_all_students()
	total = len(students)
	candidates = list(students)
	specified_last_name, specified_first_name = '', None

	try:
		while len(candidates) > 1:
			# Possibly output if we have filtered any
			if len(candidates) < total:
				print('Possible students:')
				for student in candidates:
					print('\t{}'.format(student.last_first_name))

			# Get user input
			if specified_first_name is None:
				specified_last_name += input("Type more of the student's last name: {}".format(specified_last_name)).lower()
			else:
				specified_first_name += input("Type more of the student's first name: {}, {}".format(specified_last_name, specified_first_name)).lower()
			
			# Filter and update hints
			candidates = filter_candidates(candidates, specified_last_name, specified_first_name)
			
			# If all options match in last name, switch to the first name
			if len(set(c.last_name.lower() for c in candidates)) == 1:
				specified_last_name = candidates[0].last_name.lower()
				specified_first_name = ''
	except KeyboardInterrupt:
		# Manually signal a cancel, so no student is returned
		return None
	
	if len(candidates) == 0:
		print('No student matched that description')
		return None
	
	return candidates[0]

def filter_candidates(candidates, specified_last_name, specified_first_name):
	'''
	Return a filtered list of candidates whose last_name (and maybe first_name)
	match. If there is a trailing space after either, the match for that portion
	must be exact.
	'''

	def filter_beginning(candidates, key, string):
		return [s for s in candidates if getattr(s, key).lower().startswith(string)]
	
	def filter_exact(candidates, key, string):
		return [s for s in candidates if getattr(s, key).lower() == string]
	
	result = None

	if specified_last_name[-1] == ' ':
		result = filter_exact(candidates, 'last_name', specified_last_name[:-1])
	else:
		result = filter_beginning(candidates, 'last_name', specified_last_name)

	if not specified_first_name is None:
		if specified_first_name[-1] == ' ':
			result = filter_exact(candidates, 'first_name', specified_first_name[:-1])
		else:
			result = filter_beginning(candidates, 'first_name', specified_first_name)
	
	return result
