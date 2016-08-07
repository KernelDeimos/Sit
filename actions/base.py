#!/usr/bin/python3

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
		
class CommandFactory(object):
	pass
