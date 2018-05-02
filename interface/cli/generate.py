#!/usr/bin/python3
import gradebook.config as config
import csv
import gradebook.gradebook as gradebook

import gradebook.interface.cli.generate_canvas_gradebook as generate_canvas_gradebook
import gradebook.interface.cli.generate_grade_sheet as generate_grade_sheet
import gradebook.interface.cli.generate_webassign_roster as generate_webassign_roster

from gradebook.interface.cli.subprogram import SubProgram


class GenerateProgram(SubProgram):
	@property
	def name(self):
		return 'generate'
	
	def apply_options(self, parser):
		parser.add_argument('item',
			choices = ['attendance', 'canvas', 'new', 'wa']
		)

	def on_run(self, args, dependencies):
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
