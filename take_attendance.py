#!/usr/bin/python3
import csv
import datetime
import gradebook.config as config
import gradebook.gradebook as gradebook

def add_parser(subparsers):
	parser = subparsers.add_parser('attendance')

	parser.add_argument('-date', default=None)

	parser.set_defaults(func=update_attendance)

def get_date(args):
	if args.date is None:
		return datetime.datetime.now().date().isoformat()
	else:
		return args.date

def update_attendance(args):
	'''
	The entry point.
	'''
	record = load_record()
	date = get_date(args)

	print('Marking record for {}'.format(date))

	if date_recorded_before(record, date):
		response = input('Date has been use to record. Continue? (Y/N) ')
		if response.lower() != 'y':
			print('Aborted')
			return
	
	students_to_mark = get_absent_students()

	# Verify these are the students
	print('\nStudents to mark as late on {}'.format(date))
	for student in students_to_mark:
		print('\t{}'.format(student.last_first_name))
	
	if input('Do you want to commit these absenses? (Y/N) ').lower() != 'y':
		print('Aborted')
		return
	
	update_record(record, students_to_mark, date)
	save_record(record)

def load_record():
	'''
	Load the attendance record as a map to lists. The key of the map is the
	student ID while the list is of the days absent.
	'''
	record = dict()

	with open(config.ATTENDANCE_PATH, 'r') as f:
		reader = csv.reader(f)
		for row in reader:
			key, data = row[0], row[1:]
			record[key] = data
	
	return record

def date_recorded_before(record, date):
	'''
	Check if the date is in any of the records.
	'''

	for id_string in record:
		if date in record[id_string]:
			return True
	
	return False

def get_absent_students():
	'''
	Interactively obtain students from the user to mark absent.  This is done by
	matching the last name. Returns a list of student ids.
	'''
	students = gradebook.get_all_students()
	absent_students = list()

	try:
		while True:
			student = get_student(students)
			if not student is None:
				if student in absent_students:
					print('Student already marked.')
				else:
					print('Marking {} as absent.'.format(student.last_first_name))
					absent_students.append(student)

			if input('{} student(s) marked. Mark another student? (Y/N) '.format(len(absent_students))).lower() != 'y':
				break
	
	except KeyboardInterrupt:
		print('Stopped collecting students')
	finally:
		return absent_students

def get_student(students):
	'''
	Check the list of students by first checking the last name, then
	first name until a unique student is found.
	'''
	total = len(students)
	candidates = list(students)
	last_name, first_name = '', None

	try:
		while len(candidates) > 1:
			# Possibly output
			if len(candidates) < total:
				print('Possible students:')
				for student in candidates:
					print('\t{}'.format(student.last_first_name))

			# Get user input
			if first_name is None:
				last_name += input("Type more of the student's last name: {}".format(last_name)).lower()
			else:
				first_name += input("Type more of the student's name: {}, {}".format(last_name, first_name)).lower()
			
			# Filter and update hints
			candidates = filter_candidates(candidates, last_name, first_name)
			
			if len(set(c.last_name.lower() for c in candidates)) == 1:
				last_name = candidates[0].last_name.lower()
				first_name = ''
	except KeyboardInterrupt:
		print('Jumping to the next student')
		return None
	
	if len(candidates) == 0:
		print('No student matched that description')
		return None
	
	return candidates[0]

def filter_candidates(candidates, last_name, first_name):
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

	if last_name[-1] == ' ':
		result = filter_exact(candidates, 'last_name', last_name[:-1])
	else:
		result = filter_beginning(candidates, 'last_name', last_name)

	if not first_name is None:
		if first_name[-1] == ' ':
			result = filter_exact(candidates, 'first_name', first_name[:-1])
		else:
			result = filter_beginning(candidates, 'first_name', first_name)
	
	return result

def update_record(record, students_to_mark, date):
	'''
	For each student listed, add this date to their record.
	'''
	for student in students_to_mark:
		if not student.student_id in record:
			record[student.student_id] = []
		if not date in record[student.student_id]:
			record[student.student_id].append(date)

def save_record(record):
	'''
	Commit record to file.
	'''
	with open(config.ATTENDANCE_PATH, 'w') as f:
		writer = csv.writer(f)
		for id_string in record:
			row = [id_string] + record[id_string]
			writer.writerow(row)

if __name__ == '__main__':
	update_attendance()
