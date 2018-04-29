#!/usr/bin/python3

import argparse
import csv
import os
import gradebook.config as config
import gradebook.gradebook as gradebook

def generate_roster(args):
	print('Creating WebAssign roster using saved roster.')
	students = gradebook.get_active_students()

	with open(config.OUTPUT_WA_ROSTER_PATH, 'w') as f:
		writer = csv.writer(f)
		writer.writerow(['firstname', 'lastname', 'email', 'password'])

		for student in students:
			writer.writerow([
				student.first_name,
				student.last_name,
				student.email,
				make_password(student)
			])

def make_password(student):
	'''
	Min length 6
	Max length 17
	Must have a capital letter and a number
	'''
	email = student.email
	if len(email) > 16:
		email = email[:16]
	
	return email.upper() + ''.join((17-len(email)) * ['0'])

