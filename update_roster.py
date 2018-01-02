#!/usr/bin/python3

# Takes a spreadsheet with the current students and modifies the roster
import config
import csv
import gradebook

def add_parser(parser):
	parser.add_argument('-missing', default='Dropped', help='How to mark students that are no longer listed.')
	parser.set_defaults(func=update_roster)

def update_roster(args):
	'''
	Compare the current students in the file with the available roster.
	'''
	updated_roster = load_hokiespa_roster()
	current_roster = gradebook.get_all_students()
	
	inactive_students = find_newly_inactive_students(updated_roster, current_roster)
	new_students = find_new_students(updated_roster, current_roster)

	if (inactive_students or new_students) and confirm_update(inactive_students, new_students):
		commit_update(current_roster, inactive_students, new_students, args.missing)
		print('Changes saved to class roster.')
	else:
		print('No changes were applied to the roster.')

def commit_update(current_roster, inactive_students, new_students, missing_status):
	'''
	Save the current roster to the file while changing the status of missing
	students and adding in the new students as active.
	'''
	# first, check for missings to change their status
	for missing_student in inactive_students:
		# Look for his entry in the current_roster
		for student in current_roster:
			if student.student_id == missing_student.student_id:
				student.status = missing_status
				break
	
	# add the other students
	for student in new_students:
		student.status = 'Active'

		current_roster.append(student)
	
	# Save to the roster file
	with open(config.ROSTER_PATH, 'w') as f:
		writer = csv.DictWriter(f, fieldnames=gradebook.Student.keys)
		writer.writeheader()
		for student in current_roster:
			writer.writerow(student.to_dictionary())

def confirm_update(inactive_students, new_students):
	'''
	Check if the user really wants to commit these updates after listing all
	changes that would be made.
	'''
	format_str = '{} {},{}'
	if inactive_students:
		print('{} students are now missing'.format(len(inactive_students)))
		for student in inactive_students:
			print(format_str.format(student.student_id, student.last_name, student.first_name))
	
	if new_students:
		print('{} students to add'.format(len(new_students)))
		for student in new_students:
			print(format_str.format(student.student_id, student.last_name, student.first_name))
	
	response = input('Do you want to commit these changes? (Y/N) ').lower()

	return response == 'y'

def find_newly_inactive_students(new, old):
	'''
	Go through the roster and see which students were present and active in the
	old roster, but are not listed in the new roster. Also add any students that
	are now listed as withdrawn that were active.

	returns - list of students that are now listed as inactive.
	'''

	new_ids = [ s.student_id for s in new ]

	inactive_students = []

	# Check all the students we were tracking before
	for old_student in old:
		# check if they are now inactive and we thought they were active
		if not old_student.student_id in new_ids and old_student.status == 'Active':
			inactive_students.append(old_student)
	
	return inactive_students

def find_new_students(new, old):
	'''
	Go through the new roster and see if any students are not in the current
	roster.

	returns - list of new students
	'''
	# TODO Skipped dropped and withdraws
	old_students = { s.student_id:s for s in old }

	new_students = []
	
	# Go through the new roster
	for new_student in new:
		# If someone is listed, but we aren't tracking them / their status
		# isn't active
		if (not new_student.student_id in old_students) or old_students[new_student.student_id].status != 'Active':
			new_students.append(new_student)

	return new_students

def load_hokiespa_roster():
	'''
	Take a loosely formatted HokieSpa roster and convert it to a list
	of student dictionaries.
	'''
	print('Loading Roster')

	implied_headers = [
		'Student ID',
		'Status',
		'Grading',
		'Last Name',
		'First Name',
		'Preferred Name',
		'Major',
		'Year',
		'Email',
		'Phone'
	]

	with open(config.INPUT_HOKIESPA_PATH, 'r') as hokiefile:
		reader = csv.reader(hokiefile)

		students = []

		for student_row in reader:
			student_data = {h: d.strip() for h,d in zip(implied_headers, student_row)}

			# Ignore any student that is now withdrawn
			if student_data['Grading'] == 'Course Withdrawal':
				continue

			students.append(gradebook.Student(student_data))
	
	return students
