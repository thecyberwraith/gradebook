from unittest import TestCase

from gradebook.dependencies.loader import DependencyLoader


class TestParseMethod(TestCase):
	def test_parses_correctly(self):
		loader = DependencyLoader('A.B.C.d.E', dict())
		module_name, class_name = loader.parse_class_string()

		self.assertEqual('A.B.C.d', module_name)
		self.assertEqual('E', class_name)
	
	def test_fails_on_empty_module(self):
		loader = DependencyLoader('A', dict())
		module_name, class_name = loader.parse_class_string()

		self.assertEqual('', module_name)
		self.assertEqual('A', class_name)

class DummyClass(object):
	def __init__(self, a=None, b=None):
		self.a, self.b = a,b

class TestLoadMethod(TestCase):
	def setUp(self):
		self.initializer = {'a': 1, 'b':'b'}
		self.class_string = 'gradebook.dependencies.test_loader.DummyClass'

	def test_passes_construction(self):
		loader = DependencyLoader(self.class_string, self.initializer)
		instance = loader.build_instance()

		self.assertEqual(self.initializer['a'], instance.a)
		self.assertEqual(self.initializer['b'], instance.b)
	
	def test_fails_on_bad_strings(self):
		loader = DependencyLoader(
			'gradebook.dependencies.test_loader.NotAClass',
			self.initializer
		)
		with self.assertRaises(Exception):
			loader.build_instance()
	
	def test_fails_on_bad_initializer(self):
		loader = DependencyLoader(self.class_string, {'c':2})
		
		with self.assertRaises(Exception):
			loader.build_instance()
