from .base import *

import time, datetime

class Drop(SitCommand):
	def set_parameters(self):
		self.minArgs = 0

	def perform_action(self, args):
		db = self.sess.get_db()
		projname = self.sess.require('project')
		taskname = self.sess.require('task')
		username = self.sess.require('user')

		print("No implementation yet")

class Main(CommandFactory):
	def make_action(self, sess):
		action = Drop(
			"drop", sess
		)
		return action
