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
	the loaded configuration. Also verify the Directory information.
	'''
	base_configuration = load_configuration_from_file(EXAMPLE_CONFIG_FILE)

	verification_sections = ['Paths', 'Directory']
	missing_paths = {section:list() for section in verification_sections}

	for section in verification_sections:
		for key in base_configuration[section]:
			if key not in configuration[section]:
				missing_paths[section].append(key)
	
	if sum(len(missing_paths[section]) for section in missing_paths) > 0:
		for section in missing_paths:
			for key in missing_paths[section]:
				logging.error('Missing {} entry "{}"'.format(section, key))
		raise KeyError('Configuration missing entries. Please fix the errors.')

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
	dirs = configuration['Directory']

	for path_name in paths:
		new_path = paths[path_name]
		new_path = os.path.join(base, new_path)
		new_path = os.path.abspath(new_path)
		path_name = '{}_PATH'.format(path_name)
		globals()[path_name.upper()] = new_path
	
	for dir_name in dirs:
		new_dir = dirs[dir_name]
		new_dir = os.path.join(base, new_dir)
		new_dir = os.path.abspath(new_dir)
		dir_name = '{}_DIR'.format(dir_name.upper())
		globals()[dir_name] = new_dir
	
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
