from tests.setup import ConfiguredSetup, TestArguments

import os

import config
import initialize

class TestInitScript(ConfiguredSetup):
	def test_clean_initialize(self):
		args = TestArguments(force=False)
		self.assertFalse(os.path.isfile(config.ROSTER_PATH))
		self.assertFalse(os.path.isfile(config.ATTENDANCE_PATH))
		self.assertFalse(os.path.isdir(config.DATA_DIR))
		self.assertFalse(os.path.isdir(config.INPUT_DIR))
		self.assertFalse(os.path.isdir(config.GRADES_DIR))
		self.assertFalse(os.path.isdir(config.OUTPUT_DIR))
		initialize.initialize_gradebook(args)
		self.assertTrue(os.path.isfile(config.ROSTER_PATH))
		self.assertTrue(os.path.isfile(config.ATTENDANCE_PATH))
		self.assertTrue(os.path.isdir(config.DATA_DIR))
		self.assertTrue(os.path.isdir(config.INPUT_DIR))
		self.assertTrue(os.path.isdir(config.GRADES_DIR))
		self.assertTrue(os.path.isdir(config.OUTPUT_DIR))
