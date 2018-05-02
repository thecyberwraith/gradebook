#!/usr/bin/python3
import argparse

import gradebook.config as config

from gradebook.interface.cli.aggregate_data import AggregateSubProgram
from gradebook.interface.cli.calculate_qca import QCASubProgram
from gradebook.interface.cli.generate import GenerateProgram
from gradebook.interface.cli.initialize import InitializationSubProgram
from gradebook.interface.cli.report import MathDepartmentReportSubProgram
from gradebook.interface.cli.take_attendance import AttendanceSubProgram
from gradebook.interface.cli.update_roster import UpdateRosterSubProgram


class Program(object):
	'''
	The entry point of the entire CLI interface program.
	'''

	SUB_PROGRAMS = [ 
		AggregateSubProgram(),
		QCASubProgram(),
		GenerateProgram(),
		InitializationSubProgram(),
		MathDepartmentReportSubProgram(),
		AttendanceSubProgram(),
		UpdateRosterSubProgram(),
	]
	RUNNABLE_KEY = 'func'

	def run(self):
		dependencies = self.fetch_dependencies()

		SUB_PROGRAMS = [
			'aggregate_data',
			'calculate_qca',
			'initialize',
			'generate',
			'report',
			'take_attendance',
			'update_roster',
		]

		parser = self.create_parser()
		arguments = parser.parse_args()

		runnable = getattr(arguments, Program.RUNNABLE_KEY, None)

		if runnable is None:
			print('No target sub_program selected.')
		else:
			runnable(arguments, dependencies)
	
	def fetch_dependencies(self):
		'''
		This is the analog of the Main method in clean architecture. All
		dependencies are specified at this point of the CLI interface. This
		dependency bundle can then be passed to subprograms for use in
		interfacing with external modules.
		'''
		config.load_configuration()

		dependencies = object()
		dependencies.hokiespa_roster_repository = None

		return dependencies

	def create_parser(self):
		'''
		Populate the command line interface arguments.
		'''
		parser = argparse.ArgumentParser()
		sub_parsers = parser.add_subparsers()

		for sub_program in Program.SUB_PROGRAMS:
			self.add_sub_program(sub_parsers, sub_program)

		return parser
	
	def add_sub_program(self, parser, sub_program):
		'''
		Given a sub program, create its own sub_parser, allow it to populate its
		options, and attach its on_run hook.
		'''
		sub_parser = parser.add_parser(sub_program.name)
		sub_program.apply_options(sub_parser)
		defaults = {
			Program.RUNNABLE_KEY: sub_program.on_run
		}
		sub_parser.set_defaults(**defaults)

if __name__ == '__main__':
	entry_point = Program()
	entry_point.run()
