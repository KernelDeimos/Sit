from .base import *

class GetTasks(SitCommand):
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
			
class GetProjects(SitCommand):
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

class Main(CommandFactory):
	def make_action(self, sess):
		action = Command("list")
		action.add_sub(GetTasks(
			"tasks", sess
		))
		action.add_sub(GetProjects(
			"projects", sess
		))
		return action
