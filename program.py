#!/usr/bin/python3
import argparse
import config
import importlib 

if __name__ == '__main__':
	import initialize
	import generate
	import aggregate_data
	import take_attendance
	import update_roster
	import calculate_qca
	import report

	parser = argparse.ArgumentParser()

	subparsers = parser.add_subparsers()
	generate.add_parser(subparsers.add_parser('generate'))
	aggregate_data.add_parser(subparsers.add_parser('aggregate'))
	take_attendance.add_parser(subparsers.add_parser('attendance'))
	update_roster.add_parser(subparsers.add_parser('update'))
	calculate_qca.add_parser(subparsers.add_parser('qca'))
	report.add_parser(subparsers.add_parser('report'))
	initialize.add_parser(subparsers.add_parser('init'))

	args = parser.parse_args()
	config.load_configuration()

	f = getattr(args, 'func', None)

	if f is None:
		print('No target subprogram selected.')
	else:
		f(args)
