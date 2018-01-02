import configparser
import logging
import os
import os.path

ENVIRONMENT_CONFIG_VARIABLE = 'GRADEBOOK_CONFIG'
DEFAULT_CONFIG_PATH = './config.ini'
EXAMPLE_CONFIG_FILE = os.path.join(os.path.dirname(__file__), 'example', 'config.ini')

def load_configuration():
	logging.basicConfig(level='DEBUG')

	config_path = get_config_path()
	configuration = load_configuration_from_file(config_path)
	verify_configuration(configuration)

	set_log_configuration(configuration)
	apply_configuration_to_globals(configuration)

def load_configuration_from_file(path):
	configuration = configparser.ConfigParser(
		interpolation = configparser.ExtendedInterpolation()
	)

	configuration.read(path)

	return configuration
	
def verify_configuration(configuration):
	'''
	Ensure that the loaded configuration has all the Paths that are present in
	the loaded configuration.
	'''
	base_configuration = load_configuration_from_file(EXAMPLE_CONFIG_FILE)
	missing_paths = []

	for key in base_configuration['Paths']:
		if key not in configuration['Paths']:
			missing_paths.append(key)
	
	if missing_paths:
		for path in missing_paths:
			logging.error('Missing Path entry "{}"'.format(path))
		raise KeyError('Configuration specified missing Paths. Please fix the errors.')

def set_log_configuration(configuration):
	log_level = configuration['General'].get('log level', None)

	if log_level is None:
		log_level = 'INFO'
	
	logging.debug('Setting log level to {}'.format(log_level))
	
	logging.basicConfig(level=log_level)
	
def get_config_path():
	'''
	The file is either specified by the environment variable
	ENVIRONMENT_CONFIG_VARIABLE, or it is searched for locally by the
	DEFAULT_CONFIG_PATH. If the file does not exist, an error is thrown.
	'''
	config_path = None

	if ENVIRONMENT_CONFIG_VARIABLE in os.environ:
		config_path = os.environ[ENVIRONMENT_CONFIG_VARIABLE]
	else:
		config_path = DEFAULT_CONFIG_PATH
	
	config_path = os.path.abspath(config_path)

	if not os.path.exists(config_path):
		raise FileNotFoundError('Configuration file "{}" does not exist.'.format(config_path)) 
	
	return config_path

def apply_configuration_to_globals(configuration):
	base = configuration['Directory']['Base']
	paths = configuration['Paths']

	for path_name in paths:
		new_path = paths[path_name]
		new_path = os.path.join(base, new_path)
		new_path = os.path.abspath(new_path)
		path_name = '{}_PATH'.format(path_name)
		globals()[path_name.upper()] = new_path
	
# The config is split into two parts: the specified and the built. In the specificed configuration, parameter and directory/filename information is provided. Full paths should not be provided in the specified configuration. In the built configuration, the values from the specified configuration are used to generate static filepaths using the build_configuration command.

def add_specific_config(name, value):
	if not name in globals():
		globals()[name] = value
		if name not in CONFIG_VARS:
			CONFIG_VARS.append(name)

### Specified configuration
CONFIG_VARS = []

# Directories for storing information (unless specified, assume current is base)
add_specific_config('BASE_DIR', '')
add_specific_config('OUTPUT_DIR', 'generated')
add_specific_config('INPUT_DIR', 'input')
add_specific_config('GRADES_DIR', 'grades')

# Standard name for program specific data
add_specific_config('ROSTER_FILENAME', 'ClassRoster.csv')
add_specific_config('ATTENDANCE_RECORD_FILENAME', 'AttendanceRecord.csv')

# Standard name for outputs
add_specific_config('ATTENDANCE_SHEET_FILENAME', 'BlankAttendanceSheet.csv')
add_specific_config('NEW_ITEM_FILENAME', 'NewGradedItem.csv')
add_specific_config('AGGREGATE_FILENAME', 'student_scores.csv')
add_specific_config('WA_ROSTER', 'wa_roster.csv')

# Standard name for external data sources as inputs
add_specific_config('WA_FILENAME', 'wa_scores.csv')
add_specific_config('CANVAS_FILENAME', 'ca.csv')
add_specific_config('HOKIESPA_INPUT_FILENAME', 'hokiespa_roster.csv')

# Standard name for external data source outputs
add_specific_config('CANVAS_OUTPUT_FILENAME', 'canvas_upload.csv')

# Grade weights
# the format for a weight entry should be 

# weight[category][assignment] = points
# weight[categeory]['weight'] = category weight

GRADE_WEIGHTS = {
	'homework': {
		'equally_scored': 10.0,
		'weight': 0.15,
		'drops': 1,
	},
	'WebAssign': {
		'equally_scored': 20.0,
		'weight': 0.05,
		'drops': 1,
	},
	'tests': {
		'Midterm 1': 39.0,
		'Midterm 2': 32.0,
		'Midterm 3': 33.0,
		'weight': 0.6,
	},
	'final': {
		'weight': 0.2,
		'Final - Free Response': 35,
		'Final - Multiple Choice': 14,
	},
}

QCA_VALUES = {
	'A':  4.0,
	'A-': 3.7,
	'B+': 3.3,
	'B':  3.0,
	'B-': 2.7,
	'C+': 2.3,
	'C':  2.0,
	'C-': 1.7,
	'D+': 1.3,
	'D':  1.0,
	'D-': 0.7,
	'F':  0.0,
}

GRADE_CUTOFFS = [
	('A',  0.92),
	('A-', 0.90),
	('B+', 0.87),
	('B',  0.82),
	('B-', 0.80),
	('C+', 0.77),
	('C',  0.73),
	('C-', 0.67),
	('D+', 0.65),
	('D',  0.63),
	('D-', 0.57),
	('F',  0.00),
]

def build_configuration():
	'''
	Use the specified configuration to build full paths.
	'''
	load_configuration()
	def real_join(*paths):
		return os.path.abspath(os.path.join(*paths))
	
	globals()['GRADES_DIR'] = real_join(BASE_DIR, GRADES_DIR)

	# Data files
	globals()['ROSTER_PATH'] = real_join(BASE_DIR, ROSTER_FILENAME)
	globals()['ATTENDANCE_PATH'] = real_join(BASE_DIR, ATTENDANCE_RECORD_FILENAME)

	# Output files
	globals()['ATTENDANCE_SHEET_PATH'] = real_join(BASE_DIR, OUTPUT_DIR, ATTENDANCE_SHEET_FILENAME)
	globals()['NEW_ITEM_PATH'] = real_join(BASE_DIR, OUTPUT_DIR, NEW_ITEM_FILENAME)
	globals()['AGGREGATE_OUTPUT'] = real_join(BASE_DIR, OUTPUT_DIR, AGGREGATE_FILENAME)
	globals()['WEBASSIGN_OUTPUT'] = real_join(BASE_DIR, OUTPUT_DIR, WA_ROSTER)
	globals()['CANVAS_OUTPUT'] = real_join(BASE_DIR, OUTPUT_DIR, CANVAS_OUTPUT_FILENAME)

	# External grade files
	globals()['CANVAS_INPUT'] = real_join(BASE_DIR, INPUT_DIR, CANVAS_FILENAME)
	globals()['WEBASSIGN_INPUT'] = real_join(BASE_DIR, INPUT_DIR, WA_FILENAME)
	globals()['HOKIESPA_INPUT'] = real_join(BASE_DIR, INPUT_DIR, HOKIESPA_INPUT_FILENAME)
