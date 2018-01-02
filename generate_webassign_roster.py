#!/usr/bin/python3

import argparse
import config
import csv
import gradebook
import os

def generate_roster(args):
	print('Creating WebAssign roster using saved roster.')
	students = gradebook.get_active_students()

	with open(config.WEBASSIGN_OUTPUT, 'w') as f:
		writer = csv.writer(f)
		writer.writerow(['Name', 'Username', 'Email', 'Role'])

		for student in students:
			writer.writerow([
				student.last_first_name,
				student.pid,
				student.email,
				'Student'
			])
