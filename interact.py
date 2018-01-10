import logging

class NameFilter(object):
	def __init__(self, last='', first=None):
		if isinstance(first, str):
			self._first = first.lower()
		else:
			self._first = first

		self._last = last.lower()
	
	@staticmethod
	def key_first(student):
		return student.name.first.lower()

	@staticmethod
	def key_last(student):
		return student.name.last.lower()

	def match(self, student):
		'''
		Return true if the student matches the filter.
		'''

		matched = False
		
		if self._last and self._last[-1] == ' ':
			matched = (NameFilter.key_last(student) == self._last[:-1])
		else:
			matched = NameFilter.key_last(student).startswith(self._last)

		if matched and self._first is not None:
			if self._first and self._first[-1] == ' ':
				matched = (NameFilter.key_first(student) == self._first[:-1])
			else:
				matched = NameFilter.key_first(student).startswith(self._first)

		return matched

	def update_filter(self, candidates):
		self.auto_complete(candidates)
		if self._first is None and len(set(NameFilter.key_last(s) for s in candidates)) == 1:
			self._last = NameFilter.key_last(candidates[0])
			self._first = ''

		if self._first is None:
			self._last += input("Type more of the student's last name: {._last}".format(self)).lower()
		else:
			self._first += input("Type more of the student's first name: {._last}, {._first}".format(self, self)).lower()

	def filter_candidates(self, candidates):
		'''
		Return a filtered list of candidates whose last_name (and maybe first_name)
		match. If there is a trailing space after either, the match for that portion
		must be exact.
		'''
		result = list(filter(self.match, candidates))

		return result
	
	def auto_complete(self, candidates):
		'''
		Fill in the maximum number of shared characters.
		'''
		self._last = self.get_shared_field(
			NameFilter.key_last,
			candidates
		)

	def get_shared_field(self, key, candidates):
		shared = key(candidates[0])
		for i in range(len(candidates)-1):
			shared = self.shared_start(
				shared,
				key(candidates[i+1])
			)
		return shared

	def shared_start(self, a, b):
		'''
		Return the characters similar at the start of two strings.
		'''
		for i in range(min([len(a), len(b)])):
			if a[i] != b[i]:
				return a[:i]
		return a[:min([len(a), len(b)])]

	
def interactive_find_student(students=None):
	'''
	Check the list of students by first checking the last name, then
	first name until a unique student is found. If a Keyboard Interrupt
	is thrown, then None is returned.
	'''
	if students is None:
		students = get_all_students()

	total = len(students)
	candidates = list(students)
	name_filter = NameFilter()

	try:
		while len(candidates) > 1:
			# Possibly output if we have filtered any
			if len(candidates) < total:
				logging.info('Possible students:')
				for student in candidates:
					logging.info('\t{}'.format(student.name.last_first))

			# Get user input
			name_filter.update_filter(candidates)

			# Filter and update hints
			candidates = name_filter.filter_candidates(candidates)
			
	except KeyboardInterrupt:
		# Manually signal a cancel, so no student is returned
		logigng.debug('Keyboard Interrupt')
		return None
	
	if len(candidates) == 0:
		logging.info('No student matched that description')
		return None
	
	logging.debug('Only found {}'.format(candidates))
	return candidates[0]
