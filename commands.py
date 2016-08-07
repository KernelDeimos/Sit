#!/usr/bin/python3

import sqlite3
import time, datetime

from actions import *

class CommandException(Exception):
	pass

class Command(object):
	def __init__(self, name):
		self.name = name
		self.subCommands = []
		self.minArgs = 0

		self.set_parameters()

	def set_parameters(self):
		pass

	def perform_action(self, args):
		name = args[0] if len(args) > 0 else ''
		raise CommandException("`"+name+"` action is undefined")

	def run(self, args):
		if (len(args) < self.minArgs):
			raise CommandException(self.name + ": Invalid argument count")
			return
		if (len(args) >= 1):
			base = args[0]
			for sub in self.subCommands:
				if (sub.get_name() == base):
					args.pop(0)
					try:
						sub.run(args)
					except CommandException as e:
						raise CommandException(self.name + ": " + str(e))
					return

		try:
			self.perform_action(args)
		except CommandException as e:
			raise CommandException(self.name + ": " + str(e))
		return

	def get_name(self):
		return self.name

	def add_sub(self, cmd):
		self.subCommands.append(cmd)

class SitCommand(Command):
	def __init__(self, name, sess):
		super(SitCommand, self).__init__(name)
		self.sess = sess

# === GO and STOP commands

class SitCommand_Go(SitCommand):
	def set_parameters(self):
		self.minArgs = 0

	def perform_action(self, args):
		projname = self.sess.get_prop('project')
		if projname is None:
			raise CommandException("No project selected")
		taskname = self.sess.get_prop('task')
		if taskname is None:
			raise CommandException("No task selected")
		username = self.sess.get_prop('user')
		if username is None:
			raise CommandException("No user selected")
		db = self.sess.get_db()
		db.start_clock(projname, taskname, username)

class SitCommand_Stop(SitCommand):
	def set_parameters(self):
		self.minArgs = 0

	def perform_action(self, args):
		projname = self.sess.get_prop('project')
		if projname is None:
			raise CommandException("No project selected")
		taskname = self.sess.get_prop('task')
		if taskname is None:
			raise CommandException("No task selected")
		username = self.sess.get_prop('user')
		if username is None:
			raise CommandException("No user selected")
		db = self.sess.get_db()
		db.stop_clock(projname, taskname, username)

class SitCommand_History(SitCommand):
	def set_parameters(self):
		self.minArgs = 0

	def perform_action(self, args):
		db = self.sess.get_db()
		projname = self.sess.require('project')
		taskname = self.sess.require('task')
		data = db.fetch_past_activities(projname, taskname)

		day_heading = None

		# Output history
		for row in data:
			day_dt = datetime.datetime.fromtimestamp(row['start'])
			day_str = day_dt.strftime("%Y-%m-%d")
			if day_str != day_heading:
				day_heading = day_str
				print('-------- '+day_heading)

			durr = datetime.timedelta(seconds=row['seconds'])
			hstr = str(durr)
			print(row['name']+': '+hstr)

class SitCommand_Commit(SitCommand):
	def set_parameters(self):
		self.minArgs = 1

	def perform_action(self, args):
		projname = self.sess.get_prop('project')
		if projname is None:
			raise CommandException("No project selected")
		taskname = self.sess.get_prop('task')
		if taskname is None:
			raise CommandException("No task selected")
		username = self.sess.get_prop('user')
		if username is None:
			raise CommandException("No user selected")
		message = args[0]
		db = self.sess.get_db()
		db.apply_activity(
			projname, taskname, username,
			message
		)


class SitCommand_Main(SitCommand):
	def set_parameters(self):
		self.minArgs = 1

class SitCommandFactory():
	def __init__(self, sess):
		self.sess = sess
		self.main = SitCommand_Main("sit", self.sess)

	def add_action(self, action_module):
		factory = action_module.Main()
		action  = factory.make_action(self.sess)
		self.main.add_sub(action)

		
	def get_sit(self):
		s = self.main
		
		# Actions with subcommands
		self.add_action(add_action)
		self.add_action(set_action)
		self.add_action(list_action)

		# Actions without subcommands
		self.add_action(status_action)

		# Actions not yet refactored
		s.add_sub(SitCommand_Go(
			"go", self.sess
		))
		s.add_sub(SitCommand_Stop(
			"done", self.sess
		))
		s.add_sub(SitCommand_Commit(
			"log", self.sess
		))
		s.add_sub(SitCommand_History(
			"history", self.sess
		))

		# Actions not yet implemented
		self.add_action(drop_action)

		return s
