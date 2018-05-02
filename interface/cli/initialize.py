import gradebook.config as config

import csv
import logging
import os.path

from gradebook.interface.cli.subprogram import SubProgram


class InitializationSubProgram(SubProgram):
	@property
	def name(self):
		return 'init'
	
	def apply_options(self, parser):
		parser.add_argument('-force',
			action='store_true',
			help='Necessary to overwrite roster and attendance data.'
		)
	
	def on_run(self, args):
		if not args.force and (os.path.exists(config.ROSTER_PATH) or os.path.exists(config.ATTENDANCE_PATH)):
			logging.warn('Must specify -force to override previous roster and attendance data.')
			return
		
		logging.info('Initializing gradebook...')

		headers = ['Student ID', 'First Name', 'Last Name', 'Email', 'Preferred Name', 'Year', 'Status', 'Major']
		with open(config.ROSTER_PATH, 'w') as csv_file:
			writer = csv.DictWriter(csv_file, headers)
			writer.writeheader()
		with open(config.ATTENDANCE_PATH, 'w'):
			pass
		
		logging.info('Gradebook initialized.')
