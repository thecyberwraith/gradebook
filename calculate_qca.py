import gradebook.config as config
import gradebook.gradebook as gradebook
import gradebook.grading as grading

def add_parser(subparsers):
	parser = subparsers.add_parser('qca')
	parser.add_argument('-verbose', action='store_true', default=False)
	parser.set_defaults(func=calculate_class_qca)

def calculate_class_qca(args):
	print('Working on it.')
	student_grades = gradebook.get_categorized_gradebook()

	grades = []
	letter_grades = []

	for student in gradebook.get_active_students():
		grade = grading.calculate_semester_grade(student, student_grades)
		letter = grading.calculate_student_letter_grade(student, student_grades)
		grades.append(grade)
		letter_grades.append(letter)
	
	scores = [config.QCA_VALUES[letter] for letter in letter_grades]

	print('Class QCA: {:.3f}'.format(sum(scores)/len(scores)))

	if args.verbose:
		show_verbose_qca_statistics(grades, letter_grades)

def show_verbose_qca_statistics(scores, letter_grades):
	'''
	Prints statistics from the scores.
	'''

	zipped_scores = list(zip(scores, letter_grades))
	zipped_scores.sort(key=lambda x: x[0])
	zipped_scores.reverse()
	
	show_letter_distribution(zipped_scores)
	show_grade_deltas(zipped_scores)

def show_letter_distribution(zipped_scores):
	print('Letter Grade Distribution')
	for letter in sorted(config.QCA_VALUES):
		print('{:<3}: {}'.format(
			letter,
			len([x for x in zipped_scores if x[1] == letter]),
		))
	print()

def show_grade_deltas(zipped_scores):
	print('Score  Grade Deltas')
	format_str = '{:>6.2%} {:<5} {:>6.2%}'

	previous_score, previous_letter = zipped_scores[0]
	data = zipped_scores[0] + (0,)
	print(format_str.format(*data))
	
	for i in range(1, len(zipped_scores),1):
		score, letter = zipped_scores[i]
		delta = previous_score - score
		output = format_str.format(
			score,
			letter,
			delta
		)
		
		if letter != previous_letter:
			output += ' *'

		print(output)
		previous_score = score
		previous_letter = letter
	print()
