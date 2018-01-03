from unittest import TestCase
from csv_io import SafeDictionary, make_safe

class TestSafeDictionary(TestCase):
	def setUp(self):
		self.test_dict = {
			'a': 1,
			'a b': 4,
			'A c': 5
		}
	
	def test_constructor(self):
		dic = SafeDictionary(self.test_dict)
	
	def test_constructor_throws_on_clash(self):
		test_dict = dict(self.test_dict)
		test_dict['A'] = 1
		with self.assertRaises(KeyError):
			SafeDictionary(test_dict)
	
	def test_iter(self):
		dic = SafeDictionary(self.test_dict)
		key_set = set(dic)

		for key in self.test_dict.keys():
			self.assertIn(key, key_set)

	def test_iter_over_safe_keys(self):
		dic = SafeDictionary(self.test_dict)
		key_set = set(dic.safe_iter())
		for correct_key in {'a', 'a_b', 'a_c'}:
			self.assertIn(correct_key, key_set)

	def test_safe_data_access(self):
		dic = SafeDictionary(self.test_dict)
		value = self.test_dict['A c']
		self.assertEqual(value, dic['A c'])
		self.assertEqual(value, dic['a c'])
		self.assertEqual(value, dic['a C'])
		self.assertEqual(value, dic['A_C'])
		self.assertEqual(value, dic['a_c'])
	
	def test_contains(self):
		dic = SafeDictionary(self.test_dict)
		self.assertIn('A c', dic)
		self.assertIn('A C', dic)
		self.assertIn('A_C', dic)

class TestDecorator(TestCase):
	def test_if_decorated_are_safe(self):
		@make_safe
		def test_func(dictionary):
			self.assertIsInstance(dictionary, SafeDictionary)
		test_func({'A b': 5})
