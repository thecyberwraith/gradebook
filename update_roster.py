#!/usr/bin/python3

# Takes a spreadsheet with the current students and modifies the roster
import csv
import logging

import config
from gradebook import get_all_students
from student import *

def add_parser(subparsers):
	parser = subparsers.add_parser('update')
	parser.set_defaults(func=update_roster)

def update_roster(args):
	'''
	Compare the current students in the file with the available roster.
	'''
	updated_roster = load_hokiespa_roster()
	current_roster = get_all_students()
	
	inactive_students = find_newly_inactive_students(updated_roster, current_roster)
	withdrawn_students = find_newly_withdrawn_students(updated_roster, current_roster)
	new_students = find_new_students(updated_roster, current_roster)

	changes = [inactive_students, withdrawn_students, new_students]

	if any(l for l in changes):
		if not confirm_update(changes):
			logging.info('Update cancelled.')
			return

		commit_update(current_roster, changes)
		logging.info('Changes saved to class roster.')
	else:
		logging.info('No changes were detected in the roster.')

def load_hokiespa_roster():
	'''
	Take a loosely formatted HokieSpa roster and convert it to a list
	of student dictionaries.
	'''
	logging.info('Loading Roster')

	implied_headers = [
		'Student ID',
		'Status',
		'Grading',
		'Last Name',
		'First Name',
		'Preferred',
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

			logging.info(student_data)
			# Manage withdrawn
			if student_data['Grading'] == 'Course Withdrawal':
				student_data['Status'] = 'Withdrawn'

			students.append(Student(student_data))
	
	return students

def confirm_update(changes):
	'''
	Check if the user really wants to commit these updates after listing all
	changes that would be made.
	'''
	titles = ['Dropped', 'Withdrawn', 'Active']

	for title, students in zip(titles, changes):
		if students:
			logging.info('{} students changed status to {}'.format(
				len(students),
				title))
			for student in students:
				logging.info('\t{}'.format(student))
	
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
		if not old_student.student_id in new_ids and old_student.status == StudentStatus.ACTIVE:
			inactive_students.append(old_student)
	
	return inactive_students

def find_newly_withdrawn_students(new, old):
	possible_newly_withdrawn = [student for student in new if student.status == StudentStatus.WITHDRAWN]
	withdrawn = []

	for student in possible_newly_withdrawn:
		# Check if we they are actually new
		for other in old:
			if other.student_id == student.student_id and other.status != StudentStatus.WITHDRAWN:
				withdrawn.append(student)

	return withdrawn

def find_new_students(new_roster, old_roster):
	old_students = { s.student_id:s for s in old_roster }

	new_students = []
	
	for new_student in new_roster:
		# If someone is listed, but we aren't tracking them / their status
		# isn't active
		if (not new_student.student_id in old_students) or old_students[new_student.student_id].status != StudentStatus.ACTIVE:
			new_students.append(new_student)

	return new_students

def commit_update(roster, changes):
	students = apply_changes(roster, changes)
	write_to_file(roster)
	
def apply_changes(roster, changes):
	dropped, withdrawn, new = changes

	for student in dropped:
		for other in roster:
			if student.student_id == other.student_id:
				other.status = StudentStatus.DROPPED
				break
	
	for student in withdrawn:
		for other in roster:
			if student.student_id == other.student_id:
				other.status = StudentStatus.WITHDRAWN

	# add the other students
	for student in new:
		student.status = StudentStatus.ACTIVE
		roster.append(student)
	
	return roster

def write_to_file(roster):
	keys = Student.keys + [StudentStatus.get_key(), StudentYear.get_key()]
	keys += ['Last Name', 'First Name', 'Preferred']

	with open(config.ROSTER_PATH, 'w') as f:

		writer = csv.DictWriter(f, fieldnames=keys)
		writer.writeheader()
		for student in roster:
			writer.writerow(student.to_dictionary())
