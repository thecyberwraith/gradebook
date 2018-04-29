#!/usr/bin/python3

# Creates an empty grade sheet with the information for the current active
# students.

import argparse
import csv
import os

import gradebook.config as config
import gradebook.gradebook as gradebook

def generate_new_graded_item():
	students = gradebook.get_active_students()

	with open(config.OUTPUT_NEW_GRADE_PATH, 'w') as f:
		writer = csv.writer(f)
		writer.writerow(['Student ID', 'Name', 'Score'])
		for student in students:
			writer.writerow([student.student_id, student.last_first_name, ''])
