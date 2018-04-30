'''
Module gradebook.interface.cli.submodule

This module provides the SubProgram abstract base class.
'''

from abc import ABCMeta, abstractmethod


class SubProgram(metaclass=ABCMeta):
	'''
	A subprogram should be able to identify itself, relay the options it
	expects to run with, and run itself when it receives those options.
	'''

	@property
	@abstractmethod
	def name(self):
		pass
	
	@abstractmethod
	def apply_options(self, parser):
		'''
		Add any necessary options to the parser provided.
		'''
		pass

	@abstractmethod
	def on_run(self, arguments):
		'''
		Method to run if this subprogram is specified.
		'''
		pass
