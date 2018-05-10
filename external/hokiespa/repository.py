'''
A lightweight class to abstract obtaining and writing of HokieSpa rosters.
'''

from abc import ABCMeta, abstractmethod


class HokieSpaRepository(metaclass=ABCMeta):
	@abstractmethod
	def import_hokiespa_roster(self):
		pass
	
	@abstractmethod
	def export_hokiespa_gradesheet(self, students):
		pass
