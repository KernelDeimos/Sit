Sit - Time Configuration Management
===================================

What is this?
-------------
I needed a simple program to keep track of my hours for freelance work, and I couldn't find anything that suited the requirements of what I had envisioned.

I have taken it upon myself to write this simple program, but there are a lot of things I'm going to need some help with from the open source community.
- The architecture is decent but it has a long way to go.
- There are many features I'm looking to add
- I have no idea of the proper way to put this together for package managers.

Most importantly, this program needs some network connectivity. The idea (if you haven't caught on) is to be similar to Git, but for time managment rather than software - it would be ideal if people could "push" their hours to one server.

I am also considering building a web interface. The decision remains whether starting a webserver will be a built-in feature or a separate program. The web interface should enable people to use a "Sit repository" without installing Sit. (websockets?)

What works so far?
------------------

Initial setup:

	$ ./sit new_example.db
	sit: Executed table generation
	NULL> add user eric
	Added user `eric`
	NULL> set user eric
	Set user to `eric`
	NULL> add project sit
	Added project `sit`
	NULL> set project sit
	Set project to `sit`
	sit> add task code
	Added task `code` to `sit`
	sit> set task code
	Set task to `code`
	sit:code>

Begin recording work hours

	$ ./sit new_example.db
	sit:code> go
	sit:code> status
	Currently tracking...
	Tracking since 2016-08-07 16:40:24: 0.00 hours

Stop recording work hours

	$ ./sit new_example.db	
	sit:code> done
	sit:code> status
	Ready to log...
	Ready since 2016-08-07 16:41:01: 0.01 hours

Log an activity

	$ ./sit new_example.db
	sit:code> log "Sit down for a bit"
	sit:code> status
	# does not output anything

View logged activities

	$ ./sit new_example.db
	sit:code> history
	-------- 2016-08-07
	Sit down for a bit: 0:00:36

Go out of the Sit console

	$ ./sit new_example.db
	sit:code> exit
	$


Features to be implemented
--------------------------
- TODO Lists for projects and tasks
- Parameters for history command
- More shortcuts
  - Starting Sit with "-u username"
  - Allow "set task projname:taskname"
- Categorical organization of tasks
- Remote repositories and user authentication

Internal Workings
-----------------
Saves data in an sqlite database using the sqlite1 module

Contributing
------------

I recommend that you send an email (eric.alex.dube@gmail.com) letting me know what you want to add to the program, and maybe a brief explanation of how you intend to implement it.

If this project gains enough interest I'll set up an IRC channel for contributors.
