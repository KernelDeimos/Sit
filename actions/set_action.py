from .base import *

class SetProject(SitCommand):
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

class SetTask(SitCommand):
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

class SetPerson(SitCommand):
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

class Main(CommandFactory):
	def make_action(self, sess):
		action = Command("set")
		action.add_sub(SetProject(
			"project", sess
		))
		action.add_sub(SetTask(
			"task", sess
		))
		action.add_sub(SetPerson(
			"user", sess
		))
		return action
