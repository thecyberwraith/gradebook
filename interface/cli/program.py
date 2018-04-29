#!/usr/bin/python3
import argparse
import importlib 

import gradebook.config as config

SUB_PROGRAMS = [
	'aggregate_data',
	'calculate_qca',
	'initialize',
	'generate',
	'report',
	'take_attendance',
	'update_roster',
]

MODULE_PREFIX = 'gradebook.'

if __name__ == '__main__':
	config.load_configuration()

	parser = argparse.ArgumentParser()

	subparsers = parser.add_subparsers()
	for module_name in SUB_PROGRAMS:
		module_name = MODULE_PREFIX + module_name
		module = importlib.import_module(module_name)
		module.add_parser(subparsers)

	args = parser.parse_args()

	f = getattr(args, 'func', None)

	if f is None:
		print('No target subprogram selected.')
	else:
		f(args)
