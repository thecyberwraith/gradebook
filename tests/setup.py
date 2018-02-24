import configparser
import functools
import importlib
import logging
import os
from tempfile import TemporaryDirectory
from unittest import TestCase

import config
import csv_io
from initialize import initialize_gradebook
from update_roster import update_roster


class TestArguments(object):
	def __init__(self, **args):
		for arg in args:
			setattr(self, arg, args[arg])


class InputControllingSetup(TestCase):
	modules = ['update_roster', 'interact']
	
	def setUp(self):
		super(InputControllingSetup, self).setUp()
		self.replace_input()
		self._inputs = list()
		self._old_input = input

	def tearDown(self):
		super(InputControllingSetup, self).tearDown()
		self.restore_input()
	
	def replace_input(self):
		for module_name in InputControllingSetup.modules:
			module = importlib.import_module(module_name)
			setattr(module, 'input', self.custom_input)
	
	def restore_input(self):
		for module_name in InputControllingSetup.modules:
			module = importlib.import_module(module_name)
			setattr(module, 'input', self._old_input)
	
	def custom_input(self, msg=None):
		return self._inputs.pop(0)
	
	def set_input(self, list_of_inputs):
		self._inputs = list_of_inputs.copy()


class ConfiguredSetup(InputControllingSetup):
	def setUp(self):
		super(ConfiguredSetup, self).setUp()
		logging.basicConfig(level='ERROR')
		self.prepare_environment()
		self.prepare_config()
	
	def prepare_environment(self):
		self._old_environ = os.environ.copy()
		self._tmpDir = TemporaryDirectory()
		self._tmpDir.__enter__()

	def prepare_config(self):
		sample_config = config.load_configuration_from_file('example/config.ini')
		grading_config = config.load_configuration_from_file('example/GradeConfig.ini')

		sample_config['Directory']['Base'] = os.path.abspath(self._tmpDir.name)
		sample_config['General']['log level'] = 'ERROR'
		sample_config['Paths']['GRADING'] = 'GradeConfig.ini'

		config_location = os.path.abspath(os.path.join(self._tmpDir.name, 'config.ini'))
		grading_location = os.path.join(
			os.path.abspath(self._tmpDir.name),
			'GradeConfig.ini')

		sample_config['Paths']['GRADING'] = grading_location

		with open(grading_location, 'w') as configfile:
			grading_config.write(configfile)
		with open(config_location, 'w') as configfile:
			sample_config.write(configfile)
		os.environ[config.ENVIRONMENT_CONFIG_VARIABLE] = config_location

		config.load_configuration()
	
	def tearDown(self):
		super(ConfiguredSetup, self).setUp()
		os.environ.clear()
		os.environ.update(self._old_environ)
		self._tmpDir.cleanup()


class ConfiguredWithHokieData(ConfiguredSetup):
	def setUp(self):
		super(ConfiguredWithHokieData, self).setUp()
		initialize_gradebook(TestArguments(force=False))
		self.prepare_sample_data()
		self.set_hokie_data(self.sample_data)
	
	def prepare_sample_data(self):
		# A set of hokie spa data
		self.sample_data = [
			[5, '', 'A-F', 'Bob', 'Joe', '', 'Ice Cream Technician', 'Freshman', 'bob@vt.edu', ''],
			[6, '', 'A-F', 'Bob', 'Sue', '', 'Ice Cream Engineer', 'Freshman Honors', 'sue@vt.edu', ''],
			[7, '', 'A-F', 'Wellington', 'Chet', '', 'Ice Cream Engineer', 'Sophomore', 'chet@vt.edu', ''],
		]
	
	def set_hokie_data(self, data):
		csv_io.write_rows(config.INPUT_HOKIESPA_PATH, data)
	
	def tearDown(self):
		super(ConfiguredWithHokieData, self).tearDown()
	

class ConfiguredWithInitialRoster(ConfiguredWithHokieData):
	def setUp(self):
		super(ConfiguredWithInitialRoster, self).setUp()
		self.set_input(['y'])
		update_roster(None)

	def tearDown(self):
		super(ConfiguredWithInitialRoster, self).tearDown()


class ConfiguredWithWebAssign(ConfiguredWithInitialRoster):
	def setUp(self):
		super(ConfiguredWithWebAssign, self).setUp()
		self.write_wa_scores()
	
	def write_wa_scores(self):
		wa_data = [
			[], [], [], [], # 4 useless headers
			['', '', '', '', '', 'WA 1', 'WA 2', 'WA 3'],
			['', '', '', '', '', '20', '20', '20'],
			[],[],[],
			['', 'bob@vt.edu', '', '', '', '0', '0', '0'],
			['', 'sue@vt.edu', '', '', '', '15', '15', '15'],
			['', 'chet@vt.edu', '', '', '', '20', '20', '20'],
		]
		csv_io.write_rows(config.INPUT_WA_SCORES_PATH, wa_data)
	
	def tearDown(self):
		super(ConfiguredWithWebAssign, self).tearDown()


class ConfiguredWithGrades(ConfiguredWithWebAssign):
	def setUp(self):
		super(ConfiguredWithGrades, self).setUp()
		self._add_grades()
	
	def _add_grades(self):
		self._add_homework()
		self._add_tests()
	
	def _add_homework(self):
		homework = [
			('Homework 1', [
					['', 5, 0],
					['', 6, 8],
					['', 7, 10],
				]
			),
			('Homework 2', [
					['', 5, 0],
					['', 6, 3],
					['', 7, 10],
				]
			),
			('Homework 3', [
					['', 5, 10],
					['', 6, 10],
					['', 7, 10],
				]
			),
		]
		homework_meta = {'equal points': 10, 'weight': 0.15}
		self._add_category('Homework', homework, homework_meta)
	
	def _add_tests(self):
		tests = [
			('Test 1', [
					['', 5, 0],
					['', 6, 20],
					['', 7, 25],
				],
			),
			('Test 2', [
				['', 5, 0],
				['', 6, 40],
				['', 7, 50],
				],
			),
		]
		tests_meta = {'weight': 0.6, 'Test 1': 25, 'Test 2': 50}
		self._add_category('Tests', tests, tests_meta)
	
	def _add_category(self, name, assignments, meta):
		directory = os.path.join(config.GRADES_DIR, name)
		os.mkdir(directory)
		self._write_meta(directory, meta)
		for assignment in assignments:
			self._write_assignment(directory, assignment)
	
	def _write_meta(self, directory, meta):
		metaconfig = configparser.ConfigParser()
		metaconfig['Meta'] = {}
		for key in meta:
			metaconfig['Meta'][key] = str(meta[key])
		filename = os.path.join(directory, 'weights.ini')
		with open(filename, 'w') as openfile:
			metaconfig.write(openfile)
	
	def _write_assignment(self, directory, assignment):
		name, data = assignment
		filename = os.path.join(directory, name+'.csv')
		csv_io.write_rows(filename, [['Student Name', 'Student ID', 'Score']] + data)

	def tearDown(self):
		super(ConfiguredWithGrades, self).tearDown()
