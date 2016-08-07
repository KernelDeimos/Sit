from .base import *

import time, datetime

class Status(SitCommand):
	def set_parameters(self):
		self.minArgs = 0

	def perform_action(self, args):
		db = self.sess.get_db()
		projname = self.sess.require('project')
		taskname = self.sess.require('task')
		username = self.sess.require('user')
		data = db.check_clock(projname, taskname, username)

		if len(data[0]) > 0:
			print("Currently tracking...")
		# Output tracking
		for row in data[0]:
			ts = int(row['start_time'])
			dt = datetime.datetime.fromtimestamp(ts)
			ds = dt.strftime("%Y-%m-%d %H:%M:%S")
			durr = time.time() - ts
			hours = durr / 60.0 / 60.0
			print('Tracking since '+str(ds), end='')
			hstr = "{0:.2f}".format(round(hours,2))
			print(': '+hstr+' hours')

		if len(data[0]) > 0 and len(data[1]) > 0:
			print()

		if len(data[1]) > 0:
			print("Ready to log...")

		# Output ready
		for row in data[1]:
			tss = int(row['start_time'])
			tse = int(row['end_time'])
			dt = datetime.datetime.fromtimestamp(tse)
			ds = dt.strftime("%Y-%m-%d %H:%M:%S")
			durr = tse - tss
			hours = durr / 60.0 / 60.0
			hstr = "{0:.2f}".format(round(hours,2))
			print('Ready since '+str(ds), end='')
			print(': '+hstr+' hours')

class Main(CommandFactory):
	def make_action(self, sess):
		action = Status(
			"status", sess
		)
		return action
