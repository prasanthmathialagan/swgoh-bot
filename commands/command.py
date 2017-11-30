from abc import ABCMeta, abstractmethod

class Command(object):

	__metaclass__ = ABCMeta

	def __init__(self, name):
		self.name = name

	@abstractmethod
	def execute(self, client, input, inventory, channel):
		pass