#!/usr/bin/python3
import config
import csv
import gradebook

import generate_canvas_gradebook
import generate_grade_sheet
import generate_webassign_roster

def add_parser(subparsers):
	parser = subparsers.add_parser('generate')

	parser.add_argument('item',
		choices = ['attendance', 'canvas', 'new', 'wa']
	)

	parser.set_defaults(func=generate_specific)

def generate_specific(args):
	print('Performing generation of type {}'.format(args.item))
	if args.item == 'attendance':
		generate_attendance_sheet(args)
	elif args.item == 'canvas':
		generate_canvas_gradebook.prepare_canvas_gradebook()
	elif args.item == 'new':
		generate_grade_sheet.generate_new_graded_item()
	elif args.item == 'wa':
		generate_webassign_roster.generate_roster(args)
	
def generate_attendance_sheet(args):
	print('Writing attendance sheet to {}')
	students = sorted(gradebook.get_active_students(), key=lambda s: s.last_name)

	with open(config.OUTPUT_ATTENDANCE_PATH, 'w') as f:
		writer = csv.writer(f)
		for student in students:
			writer.writerow([student.name])
