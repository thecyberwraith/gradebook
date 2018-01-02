#!/usr/bin/python3
'''
script aggregate_data

Provide course statistics with the provided data (including WebAssign data). An
aggregate csv file is provided with the students' current scores, as well as
aggregate assignment data printed to the screen.
'''
import config
import gradebook
import grading

def add_parser(parser):
	parser.add_argument('-student', action='store_true', help='Flag to enable further statistics on a single student.')
	parser.add_argument('-nowrite', action='store_true', help='Flag to disable generation of the aggregate file.')
	parser.add_argument(
		'-extrapolate',
		dest='category',
		default=None,
		help='Flag to enable output columns of maximum minimum and expected grades. The average it taken from the supplied category.',
	)
	parser.set_defaults(func=aggregate_data)

def aggregate_data(args):

	# Aggregate all the scores to a single gradebook
	categorized_gradebook = gradebook.get_categorized_gradebook()

	if args.category and not args.category in categorized_gradebook:
		print('Catetory "{}" is not in the gradebook.'.format(args.category))
		exit()

	# Ensure there is a scoring available
	grading.verify_gradebook_weights(categorized_gradebook)

	# Report statistics from the gradebook
	if not args.nowrite:
		write_student_scores(categorized_gradebook, args.category)

	print_class_scores(categorized_gradebook)

	if args.student:
		print_individual_student_scores(categorized_gradebook)

def write_student_scores(categorized_gradebook, extrapolate_category):
	'''
	Write out each student's score and letter grade to the configured file. If
	include_bounds is true, then extrapolate the grades for the end of the
	semester and include them in the gradebook.
	'''

	print('Writing out individual scores to file...')
	header = ['Name', 'Score']
	if extrapolate_category:
		header.extend(['Min', 'Avg', 'Max'])

	with open(config.AGGREGATE_OUTPUT, 'w') as output:
		import csv

		writer = csv.writer(output)
		writer.writerow(header)
		for student in gradebook.get_active_students():
			data = [
				student.name,
				grading.calculate_semester_grade(student, categorized_gradebook)
			]
			if extrapolate_category:
				data.extend(
					grading.extrapolate_scores(
						student,
						categorized_gradebook,
						extrapolate_category
					)
				)

			writer.writerow(data)
	print('\tDone')

def print_class_scores(categorized_gradebook):
	'''
	Unlike the above, which calculates the total grade of individual students,
	this method goes through each assignment and calculates the average score
	across all students. This score is printed to the screen.
	'''
	students = gradebook.get_active_students()

	for category in categorized_gradebook:
		print_class_category_scores(
			students,
			categorized_gradebook,
			category
		)
	
	print_class_average(students, categorized_gradebook)

def print_class_category_scores(students, gradebook, category):
	'''
	Given a single category, present the assignments (alphabetized) and the
	average class scores for each.
	'''
	print('\nCategory {}'.format(category))
	
	for assignment in sorted(gradebook[category].keys()):
		print('\t{:>6.2f}%  {}'.format(
			100*get_assignment_average(
				students,
				gradebook,
				category,
				assignment
				),
			assignment,
			)
		)

def get_assignment_average(students, gradebook, category, assignment):
	'''
	Calculate the average for all students on the particular assignment.
	'''
	value = 0.0
	count = 0.0
	for student in students:
		value += grading.calculate_assignment_grade(
			student,
			gradebook,
			category,
			assignment
		)
		count += 1
	
	return value / count

def print_class_average(students, categorized_gradebook):
	'''
	Calculate and print the average for the entire class.
	'''
	value = 0.0
	count = 0.0

	for student in students:
		value += grading.calculate_semester_grade(student, categorized_gradebook)
		count += 1

	print('\nAverage {}'.format(100*value/count))

def print_individual_student_scores(categorized_gradebook):

	student = gradebook.interactive_find_student()

	if student is None:
		print('No student found.')
		exit()
	
	print('Enrolled Student {}'.format(student.last_first_name))

	for category in categorized_gradebook:
		print(
			'\nCategory {}: {:.2f}'.format(
				category,
				100*grading.calculate_category_grade(
					student,
					categorized_gradebook,
					category
				)
			)
		)

		for assignment in sorted(categorized_gradebook[category]):
			percentage = grading.calculate_assignment_grade(
				student,
				categorized_gradebook,
				category,
				assignment)
			print('\t{:>6.2f}% {}'.format(100*percentage, assignment))
