from .base import *

class AddUser(SitCommand):
	def set_parameters(self):
		self.minArgs = 1

	def perform_action(self, args):
		db = self.sess.get_db()
		username = args[0]
		db.add_person(username)
		print("Added user `"+username+"`")

class AddProject(SitCommand):
	def set_parameters(self):
		self.minArgs = 1

	def perform_action(self, args):
		db = self.sess.get_db()
		projname = args[0]
		db.add_project(projname)
		print("Added project `"+projname+"`")

class AddTask(SitCommand):
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

class Main(CommandFactory):
	def make_action(self, sess):
		action = Command("add")
		action.add_sub(AddUser(
			"user", sess
		))
		action.add_sub(AddProject(
			"project", sess
		))
		action.add_sub(AddTask(
			"task", sess
		))
		return action
