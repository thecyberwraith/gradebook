#!/usr/bin/python3
import config
import gradebook

import argparse
import csv
import os
import re

def prepare_canvas_gradebook():
	'''
	Load all grades for all students, then write out a CSV for Canvas.
	'''
	print('Starting')
	categorized_gradebook = gradebook.get_categorized_gradebook()
	write_canvas_gradebook(categorized_gradebook)

def write_canvas_gradebook(categorized_gradebook):
	'''
	Take the loaded grades and write them into a csv that Canvas understands.
	'''
	# Track IDs
	student_id_dict, assignment_id_dict = get_canvas_ids()

	canvas_grades = create_canvas_gradebook(
		categorized_gradebook,
		assignment_id_dict
	)

	# Keep an order
	assignments_list = list(canvas_grades.keys())

	with open(config.OUTPUT_CANVAS_PATH, 'w') as f:
		writer = csv.writer(f)

		# Write the headers to identify students
		# SIS Login ID = PID
		# SIS User ID = student id
		# Name = first last
		identification_header = ['Student', 'ID', 'SIS User ID', 'SIS Login ID', 'Section']
		writer.writerow(identification_header + assignments_list)

		# Gotta write those points...
		points = ['Points Possible'] + ([''] * (len(identification_header) - 1))
		points_map = get_points_map()
		points += [points_map[b] for b in assignments_list]
		writer.writerow(points)

		for student in gradebook.get_active_students():
			write_student(writer, student, student_id_dict, canvas_grades, assignments_list)
	
def write_student(writer, student, id_dict, canvas_grades, assignments_list):
	canvas_id = None

	try:
		canvas_id = id_dict[student.student_id]
	except KeyError:
		print('Unable to find WA id for student {}'.format(student))

	# idenfification
	data = [student.last_first_name, canvas_id, student.student_id, student.pid]
	data += ['MATH_2204_85460_201709']

	# grades
	for assignment in assignments_list:
		try:
			data.append(canvas_grades[assignment][student.student_id])
		except KeyError:
			print('Unable to find entry for {} ({}) in {}'.format(student.name, student.student_id, assignment))
			print('Aborting.')
			exit()

	writer.writerow(data)

def create_canvas_gradebook(categorized_gradebook, assignment_id_dict):
	'''
	Make a quickly searchable dictionary representing the gradebook for all
	graded items. This includes making the correct headers.
	'''
	
	canvas_grades = dict()
	all_books = dict()

	# Copy grades to a single leveled gradebook
	for group in categorized_gradebook.values():
		all_books.update(**group)

	# Get the proper name for each assignment that Canvas will understand
	for name, book in all_books.items():
		try:
			canvas_id = assignment_id_dict[name]
		except:
			print('Unable to find equivalent to "{}" in canvas file.'.format(name))
			exit()

		canvas_grades[canvas_id] = book

	return canvas_grades

def get_canvas_ids():
	'''
	Canvas has its own ids for students, even if we use the PID. So we load an
	old gradebook and make a dictionary converting VT IDs to Canvas IDs.
	Furthermore, you cannot upload a grade unless you know the Canvas ID for
	that item. Thus, we can read the headers to parse this information,
	assuming your name matches what Canvas has.

	return - a tuple of two dicts:
		dict1 - a map from PID to Canvas ID for students
		dict2 - a map from assignment names to the full quiz name with ID
	'''
	student_id_dict = dict()
	assignment_id_dict = dict()

	with open(config.INPUT_CANVAS_PATH, 'r') as f:
		reader = csv.DictReader(f)
		for row in reader:
			student_id_dict[row['SIS User ID']] = row['ID']

		# Grab all fields
		fields = list(reader.fieldnames)

		# Make a regex to identify the true name from a canvas name-id pairing
		reg = re.compile(r'(.*) \(\d+\)')

		for field in fields:
			match = reg.match(field)
			if match:
				# If it has an id, add an assignment mapping (1=first matched
				# group, 0=the whole matched string)
				assignment_id_dict[match.group(1)] = field
		
	return student_id_dict, assignment_id_dict

def get_points_map():
	'''
	Canvas forces us to list the number of points for an assignment. This
	function finds that amount by parsing the example Canvas sheet.
	'''
	points_map = dict()

	with open(config.INPUT_CANVAS_PATH, 'r') as f:
		reader = csv.reader(f)
		assignments_row = reader.__next__()
		points_row = reader.__next__()
		for assignment, points in zip(assignments_row, points_row):
			points_map[assignment] = points
	
	return points_map
