'''
module grading

Implements methods that calculate a student's average for the course and can
extrapolate from there.
'''
import gradebook.config as config

def calculate_semester_grade(student, gradebook):
	'''
	Given a single student, calculate the student's final weighted grade. Note:
	if the sum of the weights is less than 100%, then the score will be scaled
	to show completion for the specified weighted categories.

	Output: grade (as a float between 0 and 1)
	'''
	score = 0.0
	weight_sum = 0.0

	for category in gradebook:
		category_info = config.GRADE_WEIGHTS[category]
		weight = category_info['weight']
		score += weight * calculate_category_grade(
			student,
			gradebook,
			category
		)
		weight_sum += weight
	
	return score / weight_sum

def calculate_category_grade(student, gradebook, category):
	'''
	We assume each element of a category is equally weighted. Calculates the
	student's grade in that category according to the configured scoring and
	drops.
	'''
	scores = []

	for assignment in gradebook[category]:
		scores.append(
			calculate_assignment_grade(
				student,
				gradebook,
				category,
				assignment
			)
		)
	
	drops = config.GRADE_WEIGHTS[category].get('drops', None)
	if drops is not None:
		for _ in range(drops):
			scores.remove(min(scores))

	return sum(scores) / (1.0 * len(scores))

def calculate_assignment_grade(student, gradebook, category, assignment):
	'''
	For a single assignment, get the student's percentage on the assignment.
	'''
	try:
		score = float(gradebook[category][assignment][student.student_id])
	except ValueError:
		score = 0.0
	
	points = config.GRADE_WEIGHTS[category].get('equally_scored')

	if points is None:
		points = config.GRADE_WEIGHTS[category][assignment]
	
	return score / points

def calculate_student_letter_grade(student, gradebook):
	score = calculate_semester_grade(student, gradebook)
	student_letter = None

	for letter, necessary_score in config.GRADE_CUTOFFS:
		if score >= necessary_score:
			student_letter = letter
			break
	
	return student_letter

def extrapolate_scores(student, gradebook, extrapolate_category):
	'''
	Given a single student, calculate what the student's maximum, minimum, and average score can be
	if the remaining weighted assignments have maximum score, minimum score, or category average score. 
	Returns the values in a tuple (min, avg, best).
	'''

	grade = calculate_semester_grade(student, gradebook)

	weight_sum = 0.0
	for category in gradebook:
		weight_sum += config.GRADE_WEIGHTS[category]['weight']
	
	worst = (weight_sum * grade)
	best = worst + (1-weight_sum)

	avg = calculate_category_grade(student, gradebook, extrapolate_category)

	print(category, student.name, avg, worst, weight_sum)
	avg = worst + (1-weight_sum)*avg

	return worst, avg, best

def verify_gradebook_weights(categorized_gradebook):
	'''
	Check the local config file for the category weights and the maximum
	points for each assignment (unless the equally_weighted key is found). If a
	category found in the gradebook is not assigned a weight, this method will
	exit the entire program.
	'''
	print('Verifying weights...')

	weights = config.GRADE_WEIGHTS.copy()
	weight_sum = 0.0

	all_good = True

	for category in categorized_gradebook:
		if not category in weights:
			print('\tCategory "{}" not found in configured grade weights.'.format(category))
			all_good = False
		else:
			if 'weight' not in weights[category]:
				print('\tCategory "{}" does not have an assigned weight.'.format(category))
				all_good = False
			else:
				weight_sum += weights[category]['weight']

			if 'equally_scored' not in weights[category]:
				for assignment in categorized_gradebook[category]:
					if assignment not in weights[category]:
						print('\tAssignment "{}" in category "{}" not found in configured grade weights'.format(
							assignment,
							category,
						))
						all_good = False

	if weight_sum < 1.0:
		print('\tWarning: the sum of weights is below 100%')
	if not all_good:
		exit()
	print('\tPassed')
