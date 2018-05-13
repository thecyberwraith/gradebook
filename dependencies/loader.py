'''
This module uses reflection and modules to load dependencies from a
configuration dictionary.
'''

from importlib import __import__ as importer


class DependencyLoader(object):
	def __init__(self, class_string, constructor_dictionary):
		self._class_string = class_string 
		self._constructor_dictionary = constructor_dictionary
	
	def build_instance(self):
		'''
		Attempts to load an instance of the configured class.
		'''
		module_name, class_name = self.parse_class_string()

		try:
			module = importer(module_name, fromlist=[class_name])
			dependency_class = getattr(module, class_name)
		except Exception as e:
			raise Exception(
				'Failed to load dependency {} from {}'.format(
					class_name,
					module_name
				)
			)
		
		return dependency_class(**self._constructor_dictionary)
	
	def parse_class_string(self):
		try:
			parts = self._class_string.split('.')
			other_parts, class_name = parts[:-1], parts[-1]
			module_name = '.'.join(other_parts)

			return  module_name, class_name
		except:
			raise Exception(
				'Failed to parse class string {}'.format(
					self._class_string
				)
			)
