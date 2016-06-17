Sit - Time Configuration Management
===================================

What is this?
-------------
I needed a simple program to keep track of my hours for freelance work, and I couldn't find anything that suited the requirements of what I had envisioned.

I have taken it upon myself to write this simple program, but there are a lot of things I'm going to need some help with from the open source community.
- The architecture is "not horrible" but it has a long way to go.
- There are many features I'm looking to add
- I have no idea of the proper way to put this together for package managers.

Most importantly, this program needs some network connectivity. The idea (if you haven't caught on) is to be similar to Git, but for time managment rather than software - it would be ideal if people could "push" their hours to one server.

I am also considering building a web interface. The decision remains whether starting a webserver will be a built-in feature or a separate program. The web interface should enable people to use a "Sit repository" without installing Sit. (websockets?)

What works so far?
------------------

Initial setup:

	$ ./sit new_example.db
	NULL> add user eric
	Added user 'eric'
	NULL> set user eric
	Set user to 'eric'
	NULL> add project sit
	Added project 'sit'
	NULL> set project sit
	Set project to 'sit'
	sit> add task code
	Added task 'code' to 'sit'
	sit> set task code
	Set task to 'code'

Begin recording work hours

	$ ./sit new_example.db
	sit:code> go
	sit:code> status
	Currently tracking...
	Tracking since 2016-06-17 13:17:39: 0.00 hours

Stop recording work hours

	$ ./sit new_example.db	
	sit:code> done
	sit:code> status
	Ready to log...
	Ready since 2016-06-17 13:18:20: 0.01 hours

Log activity

	$ ./sit new_example.db
	sit:code> log "Sit down for a bit"
	sit:code> status
	# does not output anything

A **very** basic history command

	$ ./sit new_exapmle.db
	site:code> history
	Sit down for a bit: 0.01 hours

Going out of the Sit console

	$ ./sit new_example.db
	sit:code> exit
	$


Features to be implemented
--------------------------
- TODO Lists
- 'history' command (like git log)
- Any network connectivity at all
- More shortcuts
  - Starting Sit with "-u username"
  - "set task projname:taskname"
- Task branches?
- User authentication

Internal Workings
-----------------
Saves data in an sqlite database using the sqlite1 module

Contributing
------------
If you only send a pull request, I can't guarentee I'll accept it (though I may).

I recommend that you send an email (eric.alex.dube@gmail.com) letting me know what you want to add to the program, and maybe a bried explanation of how you intend to implement it.

If this project gains enough interest I'll set up an IRC channel for contributors.
