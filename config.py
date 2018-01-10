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
	the loaded configuration. Also verify the Directory information. Then check
	if the grading scheme is properly configured.
	'''
	def contains_section_key(configuration, section, key):
		return (section in configuration) and (key in configuration[section])

	base_configuration = load_configuration_from_file(EXAMPLE_CONFIG_FILE)

	verification_sections = ['Paths', 'Directory']
	missing_paths = {section:list() for section in verification_sections}

	for section in verification_sections:
		for key in base_configuration[section]:
			if not contains_section_key(configuration, section, key):
				missing_paths[section].append(key)
	
	if sum(len(missing_paths[section]) for section in missing_paths) > 0:
		for section in missing_paths:
			for key in missing_paths[section]:
				logging.error('Missing {} entry "{}"'.format(section, key))
		raise KeyError('Configuration missing entries. Please fix the errors.')
	
	verify_grading_configuration(configuration)

def verify_grading_configuration(configuration):
	'''
	Ensure there is a WebAssignWeight and the letters of QCA and Cutoff
	sections match.
	'''
	grade_config = None

	try:
		grade_config = load_configuration_from_file(
			os.path.join(
				configuration['Directory']['Base'],
				configuration['Paths']['Grading']
			)
		)
	except Exception as e:
		raise FileNotFoundError('Failed to open grading config: {}'.format(e))
		
	if not (('General' in grade_config) and ('WebAssignWeight' in grade_config['General'])):
		raise KeyError('Need to specify "WebAssignWeight" in the grading config file.')
	
	if not (('QCA' in grade_config) and ('Cutoff' in grade_config)):
		raise KeyError('QCA and Cutoff sections must be specified in grading config file.')
	
	for key in grade_config['QCA']:
		if not key in grade_config['Cutoff']:
			raise KeyError('There are missing letters in the Cutoff section of the grading config file.')

	for key in grade_config['Cutoff']:
		if not key in grade_config['QCA']:
			raise KeyError('There are missing letters in the QCA section of the grading config file.')

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

	def apply_to_globals(section, base, name_format):
		for path_name in section:
			new_path = section[path_name]
			new_path = os.path.join(base, new_path)
			new_path = os.path.abspath(new_path)

			path_name = name_format.format(path_name)
			path_name = path_name.upper()

			globals()[path_name] = new_path

	apply_to_globals(configuration['Paths'], base, '{}_PATH')
	apply_to_globals(configuration['Directory'], base, '{}_DIR')
