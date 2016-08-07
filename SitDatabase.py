import time

class SitDatabase:
	def __init__(self, conn):
		self.conn = conn
	def generate_tables(self):
		c = self.conn.cursor()
		c.execute('''
			CREATE TABLE IF NOT EXISTS projects (
				projname TEXT PRIMARY KEY,
				name TEXT
			);
		''')
		c.execute('''
			CREATE TABLE IF NOT EXISTS tasks (
				projname TEXT NOT NULL,
				taskname TEXT NOT NULL,

				FOREIGN KEY(projname) REFERENCES projects(projname),
				PRIMARY KEY (projname, taskname)
			);
		''')
		c.execute('''
			CREATE TABLE IF NOT EXISTS persons (
				username TEXT PRIMARY KEY,
				name TEXT,

				curr_projname TEXT,
				curr_taskname TEXT,

				FOREIGN KEY(curr_projname)
				REFERENCES projects(projname),
				FOREIGN KEY(curr_taskname)
				REFERENCES tasks(taskname)
			);
		''')
		c.execute('''
			CREATE TABLE IF NOT EXISTS activities (
				projname TEXT NOT NULL,
				taskname TEXT NOT NULL,
				activ_id INTEGER,

				name TEXT,

				FOREIGN KEY(projname) REFERENCES projects(projname),
				FOREIGN KEY(taskname) REFERENCES tasks(taskname),
				PRIMARY KEY (projname, taskname, activ_id)
			);
		''')
		c.execute('''
			CREATE TABLE IF NOT EXISTS hours (
				projname TEXT NOT NULL,
				taskname TEXT NOT NULL,
				hours_id INTEGER,

				activ_id INTEGER,
				assoc_user TEXT,

				start_time INTEGER,
				end_time INTEGER,

				FOREIGN KEY(activ_id) REFERENCES activities(activ_id),
				FOREIGN KEY(assoc_user) REFERENCES persons(username),

				FOREIGN KEY(projname) REFERENCES projects(projname),
				FOREIGN KEY(taskname) REFERENCES tasks(taskname),
				PRIMARY KEY (projname, taskname, hours_id)
			);
		''')
		self.conn.commit()
		print("sit: Executed table generation")
	def add_person(self, username):
		c = self.conn.cursor()
		inputs = (username,)
		c.execute('INSERT INTO persons (username) VALUES (?)', inputs)
		self.conn.commit()
		pass
	def add_project(self, projname):
		c = self.conn.cursor()
		inputs = (projname,)
		c.execute('INSERT INTO projects (projname) VALUES (?)', inputs)
		self.conn.commit()
		pass
	def add_task(self, projname, taskname):
		c = self.conn.cursor()
		# Get ID for task
		inputs = (projname, taskname,)
		c.execute('INSERT INTO tasks (projname, taskname) VALUES (?,?)', inputs)
		self.conn.commit()
	def start_clock(self, projname, taskname, username):
		c = self.conn.cursor()
		# Get ID for clock
		inputs = (projname, taskname)
		c.execute('''SELECT MAX(hours_id) AS id FROM hours
			WHERE projname=? AND taskname=?''', inputs)
		hours_id = 1
		last_hours_row = c.fetchone()
		if last_hours_row[0] is not None:
			hours_id = last_hours_row[0]+1
		# Perform INSERT
		start_time = time.time()
		inputs = (start_time, projname, taskname, hours_id, username)
		c.execute('''INSERT INTO hours
			(start_time, projname, taskname, hours_id, assoc_user)
			VALUES (?,?,?,?,?)''', inputs)
		self.conn.commit()
	def stop_clock(self, projname, taskname, username):
		c = self.conn.cursor()
		end_time  = time.time()
		inputs = (end_time, projname, taskname, username)
		c.execute('''UPDATE hours SET end_time=?
			WHERE projname=?
			AND taskname=?
			AND assoc_user=?
			AND end_time IS NULL
			''', inputs)
		self.conn.commit()
	def check_clock(self, projname, taskname, username):
		c = self.conn.cursor()
		inputs = (projname, taskname, username)
		# FETCH CURRENTLY TRACKING
		c.execute('''SELECT start_time FROM hours
			WHERE projname=?
			AND taskname=?
			AND assoc_user=?
			AND end_time IS NULL''', inputs)
		tracking = []
		for row in c.fetchall():
			datum = {}
			datum['start_time'] = row[0]
			tracking.append(datum)
		# FETCH READY-TO-LOG
		c.execute('''SELECT start_time, end_time FROM hours
			WHERE projname=?
			AND taskname=?
			AND assoc_user=?
			AND end_time IS NOT NULL
			AND activ_id IS NULL''', inputs)
		ready = []
		for row in c.fetchall():
			datum = {}
			datum['start_time'] = row[0]
			datum['end_time'] = row[1]
			ready.append(datum)
		return (tracking, ready)
	def apply_activity(self, projname, taskname, username, message):
		c = self.conn.cursor()
		# Get ID for activity
		inputs = (projname, taskname)
		c.execute('''SELECT MAX(activ_id) AS id FROM activities
			WHERE projname=? AND taskname=?''', inputs)
		activ_id = 1
		last_hours_row = c.fetchone()
		if last_hours_row[0] is not None:
			activ_id = last_hours_row[0]+1
		# Create the activity
		inputs = (projname, taskname, activ_id, message)
		c.execute('''INSERT INTO activities
			(projname, taskname, activ_id, name)
			VALUES (?,?,?,?)
			''', inputs)
		# Set activity to all unset hours
		inputs = (activ_id, projname, taskname, username)
		c.execute('''UPDATE hours SET activ_id=?
			WHERE projname=?
			AND taskname=?
			AND assoc_user=?
			AND end_time IS NOT NULL
			AND activ_id IS NULL
			''', inputs)
		self.conn.commit()

	def save_user_proj(self, username, projname):
		c = self.conn.cursor()
		inputs = (projname, username)
		c.execute('''UPDATE persons SET curr_projname=?
			WHERE username=?
			''', inputs)
		self.conn.commit()
	def save_user_task(self, username, projname, taskname):
		c = self.conn.cursor()
		inputs = (projname, taskname, username)
		c.execute('''UPDATE persons SET
			curr_projname=?,
			curr_taskname=?
			WHERE username=?
			''', inputs)
		self.conn.commit()

	def load_user(self, username):
		c = self.conn.cursor()
		# Get ID for clock
		inputs = (username,)
		c.execute('''SELECT curr_projname, curr_taskname FROM persons
			WHERE username=?''', inputs)
		row = c.fetchone()
		data = {}
		data['projname'] = row[0]
		data['taskname'] = row[1]
		return data

	def check_proj_exists(self, projname):
		c = self.conn.cursor()
		# Get ID for clock
		inputs = (projname,)
		c.execute('''SELECT * FROM projects
			WHERE projname=?''', inputs)
		return len(c.fetchall()) > 0
	def check_task_exists(self, projname, taskname):
		c = self.conn.cursor()
		# Get ID for clock
		inputs = (projname,taskname,)
		c.execute('''SELECT * FROM tasks
			WHERE projname=? AND taskname=?''', inputs)
		return len(c.fetchall()) > 0

	def fetch_tasks(self, projname):
		c = self.conn.cursor()
		# Get ID for clock
		inputs = (projname,)
		c.execute('''SELECT taskname FROM tasks
			WHERE projname=?''', inputs)
		data = []
		for row in c.fetchall():
			datum = {}
			datum['taskname'] = row[0]
			data.append(datum)
		return data

	def fetch_projects(self):
		c = self.conn.cursor()
		# Get ID for clock
		# inputs = ()
		c.execute('''SELECT projname FROM projects
			WHERE 1=1''')
		data = []
		for row in c.fetchall():
			datum = {}
			datum['projname'] = row[0]
			data.append(datum)
		return data


	def fetch_past_activities(self, projname, taskname):
		# List to return
		activities = []
		# Get cursor and input list
		c = self.conn.cursor()
		inputs = (projname, taskname,)
		# Fetch all activities within this task
		c.execute('''SELECT name, activ_id FROM activities
			WHERE projname=?
			AND taskname=?
			''', inputs)
		for row in c.fetchall():
			name = row[0]
			activ_id = row[1]
			inputs = (projname, taskname, activ_id)
			seconds = 0
			begints = -1
			# Fetch all hours within this activity
			c_hours = self.conn.cursor()
			c_hours.execute('''SELECT start_time, end_time FROM hours
				WHERE projname=?
				AND taskname=?
				AND activ_id=?''', inputs)
			for hour in c_hours.fetchall():
				start_time = hour[0]
				end_time   = hour[1]
				seconds += int(end_time - start_time)
				if start_time < begints or begints == -1:
					begints = start_time
			# Fetch all hours within this activity
			# c.execute('''SELECT SUM(end_time - start_time) FROM hours
			# 	WHERE projname=?
			# 	AND taskname=?
			# 	AND activ_id=?''', inputs)
			# seconds = int(c.fetchone()[0])
			act = {}
			act['name'] = name
			act['seconds'] = seconds
			act['start'] = begints
			activities.append(act);
		return activities
