#!/usr/bin/python3
import argparse
import config
import importlib 

SUB_PROGRAMS = [
	'aggregate_data',
	'calculate_qca',
	'initialize',
	'generate',
	'report',
	'take_attendance',
	'update_roster',
]

if __name__ == '__main__':
	config.load_configuration()

	parser = argparse.ArgumentParser()

	subparsers = parser.add_subparsers()
	for module_name in SUB_PROGRAMS:
		module = importlib.import_module(module_name)
		module.add_parser(subparsers)

	args = parser.parse_args()

	f = getattr(args, 'func', None)

	if f is None:
		print('No target subprogram selected.')
	else:
		f(args)
