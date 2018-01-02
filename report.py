import config
from csv_io import write_dataset, load_csv_as_dict
from gradebook import get_all_students, get_categorized_gradebook
from grading import calculate_semester_grade, calculate_student_letter_grade

def add_parser(parser):
	parser.add_argument('-forcenames', action='store_true')
	parser.set_defaults(func=build_report)

def build_report(args):
	students = get_all_students()
	students = list(filter(lambda x: x.status in ['Active', 'Withdrawn'], students))

	gradebook = get_categorized_gradebook()
	attendance_record = get_attendance_record()

	dataset = []

	for student in students:
		dataset.append(gather_report_data(student, gradebook, attendance_record, args.forcenames))
	
	sorted_dataset = sort_dataset_with_scores(dataset)

	write_dataset('generated/report.csv', sorted_dataset)

def gather_report_data(student, gradebook, attendance_record, include_name):
	student_data = dict()
	student_data['ID'] = student.student_id
	student_data['Major'] = student.major
	if include_name:
		student_data['Name'] = student.name

	if student.status == 'Withdrawn':
		student_data['Grade'] = 'W'
		student_data['Absences'] = ''
		student_data['Score'] = -1
	else:
		student_data['Grade'] = calculate_student_letter_grade(student, gradebook)
		student_data['Absences'] = len(attendance_record.get(student.student_id, list()))
		student_data['Score'] = calculate_semester_grade(student, gradebook)
	
	return student_data

def sort_dataset_with_scores(dataset):
	sorted_data = list(reversed(sorted(dataset, key=lambda x: x['Score'])))
	
	for student_data in sorted_data:
		del student_data['Score']
	
	return sorted_data

def get_attendance_record():
	return load_csv_as_dict(config.ATTENDANCE_PATH)
