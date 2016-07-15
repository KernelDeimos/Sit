#!/usr/bin/python3

import sqlite3
import time, datetime

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

# === SUBCOMMANDS FOR ADD

class SitCommand_AddUser(SitCommand):
	def set_parameters(self):
		self.minArgs = 1

	def perform_action(self, args):
		db = self.sess.get_db()
		username = args[0]
		db.add_person(username)
		print("Added user `"+username+"`")

class SitCommand_AddProject(SitCommand):
	def set_parameters(self):
		self.minArgs = 1

	def perform_action(self, args):
		db = self.sess.get_db()
		projname = args[0]
		db.add_project(projname)
		print("Added project `"+projname+"`")

class SitCommand_AddTask(SitCommand):
	def set_parameters(self):
		self.minArgs = 1

	def perform_action(self, args):
		# localize session info
		projname = self.sess.get_prop('project')
		if projname is None:
			raise CommandException("No project selected")
		db = self.sess.get_db()
		taskname = args[0]
		try:
			db.add_task(projname, taskname)
			print("Added task `"+taskname+"` to `"+projname+"`")
		except sqlite3.IntegrityError:
			print("Task already exists")


# === SUBCOMMANDS FOR SET

class SitCommand_SetProject(SitCommand):
	def set_parameters(self):
		self.minArgs = 1

	def perform_action(self, args):
		# localize db and params
		db = self.sess.get_db()
		projname = args[0]
		# Ensure project exists
		if not db.check_proj_exists(projname):
			raise CommandException("Project does not exist")
		# Update user profile
		username = self.sess.get_prop('user')
		if username is None:
			raise CommandException("No user selected")
		try:
			db.save_user_task(username, projname, None)
		except sqlite3.IntegrityError:
			raise CommandException("Project does not exist")
		# Update session
		self.sess.set_prop('project',projname)
		self.sess.set_prop('task',None)
		print("Set project to `"+projname+"`")

class SitCommand_SetTask(SitCommand):
	def set_parameters(self):
		self.minArgs = 1

	def perform_action(self, args):
		# localize db and params
		db = self.sess.get_db()
		projname = self.sess.get_prop('project')
		if projname is None:
			raise CommandException("No project selected")
		taskname = args[0]
		# Ensure task exists
		if not db.check_task_exists(projname, taskname):
			raise CommandException("Task does not exist")
		# Update user profile
		username = self.sess.get_prop('user')
		if username is None:
			raise CommandException("No user selected")
		try:
			db.save_user_task(username, projname, taskname)
		except sqlite3.IntegrityError:
			raise CommandException("Task does not exist")
		# Update session
		self.sess.set_prop('task',taskname)
		print("Set task to `"+taskname+"`")

class SitCommand_SetPerson(SitCommand):
	def set_parameters(self):
		self.minArgs = 1

	def perform_action(self, args):
		# localize db and params
		db = self.sess.get_db()
		username = args[0]
		#
		userinfo = db.load_user(username)
		#
		self.sess.set_prop('user',username)
		project = userinfo['projname']
		task = userinfo['taskname']
		if project is not None:
			self.sess.set_prop('project',project)
		if task is not None:
			self.sess.set_prop('task',task)
		print("Set user to `"+username+"`")

# === GET commands

class SitCommand_GetTasks(SitCommand):
	def set_parameters(self):
		self.minArgs = 0

	def perform_action(self, args):
		# localize db and params
		db = self.sess.get_db()
		projname = self.sess.get_prop('project')
		if projname is None:
			raise CommandException("No project selected")
		#
		data = db.fetch_tasks(projname)
		#
		for row in data:
			print("Task: "+row['taskname'])

class SitCommand_GetProjects(SitCommand):
	def set_parameters(self):
		self.minArgs = 0

	def perform_action(self, args):
		# localize db and params
		db = self.sess.get_db()
		#
		data = db.fetch_projects()
		#
		for row in data:
			print("Project: "+row['projname'])

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

class SitCommand_Status(SitCommand):
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

class SitCommand_History(SitCommand):
	def set_parameters(self):
		self.minArgs = 0

	def perform_action(self, args):
		db = self.sess.get_db()
		projname = self.sess.require('project')
		taskname = self.sess.require('task')
		data = db.fetch_past_activities(projname, taskname)

		# Output history
		for row in data:
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

	def get_add(self):
		add = Command("add")
		add.add_sub(SitCommand_AddUser(
			"user", self.sess
		))
		add.add_sub(SitCommand_AddProject(
			"project", self.sess
		))
		add.add_sub(SitCommand_AddTask(
			"task", self.sess
		))
		return add

	def get_set(self):
		_set = Command("set")
		_set.add_sub(SitCommand_SetProject(
			"project", self.sess
		))
		_set.add_sub(SitCommand_SetTask(
			"task", self.sess
		))
		_set.add_sub(SitCommand_SetPerson(
			"user", self.sess
		))
		return _set

	def get_list(self):
		_get = Command("list")
		_get.add_sub(SitCommand_GetTasks(
			"tasks", self.sess
		))
		_get.add_sub(SitCommand_GetProjects(
			"projects", self.sess
		))
		return _get
		
	def get_sit(self):
		s = SitCommand_Main("sit", self.sess)
		s.add_sub(self.get_add())
		s.add_sub(self.get_set())
		s.add_sub(self.get_list())

		s.add_sub(SitCommand_Go(
			"go", self.sess
		))
		s.add_sub(SitCommand_Stop(
			"done", self.sess
		))
		s.add_sub(SitCommand_Commit(
			"log", self.sess
		))
		s.add_sub(SitCommand_Status(
			"status", self.sess
		))
		s.add_sub(SitCommand_History(
			"history", self.sess
		))

		return s
