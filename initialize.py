import config

import csv
import logging
import os.path

def add_parser(subparsers):
	parser = subparsers.add_parser('init')
	parser.add_argument('-force',
		action='store_true',
		help='Necessary to overwrite roster and attendance data.'
	)

	parser.set_defaults(func=initialize_gradebook)

def initialize_gradebook(args):
	if not args.force and (os.path.isfile(config.ROSTER_PATH) or os.path.isfile(config.ATTENDANCE_PATH)):
		logging.warn('Must specify -force to override previous roster and attendance data.')
		return
	
	logging.info('Initializing gradebook...')

	ensure_directories()
	create_files()
	
	logging.info('Gradebook initialized.')

def ensure_directories():
	dir_names = [name for name in dir(config) if name[-3:] == 'DIR']
	for name in dir_names:
		if not os.path.isdir(getattr(config, name)):
			os.mkdir(getattr(config, name))
			logging.debug('Making directory {}'.format(getattr(config, name)))

def create_files():
	headers = ['Student ID', 'First Name', 'Last Name', 'Email', 'Preferred Name', 'Year', 'Status', 'Major']

	# Refresh the roster and attendance
	with open(config.ROSTER_PATH, 'w') as csv_file:
		writer = csv.DictWriter(csv_file, headers)
		writer.writeheader()
		logging.debug('Writing blank roster.')
	with open(config.ATTENDANCE_PATH, 'w'):
		logging.debug('Writing new attendance record.')
