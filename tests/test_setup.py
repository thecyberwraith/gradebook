import config
from tests.setup import *

class TestSetupClasses(TestCase):
	def test_input_controlling(self):
		tmp = InputControllingSetup()
		tmp.setUp()
		tmp.tearDown()
	
	def test_configured_setup(self):
		tmp = ConfiguredSetup()
		tmp.setUp()
		tmp.tearDown()

	def test_hokie_data(self):
		tmp = ConfiguredWithHokieData()
		tmp.setUp()
		tmp.tearDown()
	
	def test_initial_roster(self):
		tmp = ConfiguredWithInitialRoster()
		tmp.setUp()
		with open(config.ROSTER_PATH) as roster:
			lines = roster.readlines()
			self.assertEqual(len(lines), 1+len(tmp.sample_data))
		tmp.tearDown()
	
	def test_web_assign(self):
		tmp = ConfiguredWithWebAssign()
		tmp.setUp()
		tmp.tearDown()
	
	def test_grades(self):
		tmp = ConfiguredWithGrades()
		tmp.setUp()
		tmp.tearDown()
