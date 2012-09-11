import database, validator, sys, re

# helpers:
def connectToDatabase():
	return database.Database('./')

# actions:
def createUser(args):
	username, firstname, lastname, email = args

	try:
		db = connectToDatabase()

		if not db.userExists(username):
			db.createUser(username, firstname, lastname, email)
		else:
			print('given username does already exist')
			return False

	except Exception, e:
		print('couldn\'t create user: "%s"' % e)
		return False

	return True

def updateUser(args):
	username, firstname, lastname, email = args

	try:
		db = connectToDatabase()

		if db.userExists(username):
			db.updateUser(username, firstname, lastname, email)
		else:
			print('couldn\'t find user: "%s"' % username)
			return False

	except Exception, e:
		print('couldn\'t update user: "%s"' % e)
		return False

	return True

def showUser(args):
	username = args[0]

	try:
		db = connectToDatabase()

		if db.userExists(username):
			firstname, lastname, email, blocked = db.getUser(username)
			print 'user........: %s\nfirstname...: %s\nlastname....: %s\nemail.......: %s\nblocked.....: %d' % (username, firstname, lastname, email, blocked)
		else:
			print('couldn\'t find user: "%s"' % username)
			return False

	except Exception, e:
		print('couldn\'t get user: "%s"' % e)
		return False

	return True

def enableUser(args):
	username = args[0]

	try:
		db = connectToDatabase()
		db.blockUser(username, 0)

	except Exception, e:
		print('couldn\'t enable user: "%s"' % e)
		return False

	return True

def disableUser(args):
	username = args[0]

	try:
		db = connectToDatabase()
		db.blockUser(username, 1)

	except Exception, e:
		print('couldn\'t disable user: "%s"' % e)
		return False

	return True

def showUsers(args):
	try:
		db = connectToDatabase()

		users = db.getUsers()

		if not users is None:
			for username, email, blocked in users:
				if blocked == 0:
					status = 'enabled'
				else:
					status = 'disabled'

				print('%s <%s>, %s' % (username, email, status))
		else:
			print('user database is empty')

	except Exception, e:
		print('couldn\'t get users: "%s"' % e)
		return False

	return True

# each action has an assigned list of argument validators & one callback function
commands = {
		'--create-user':
		{
			# args: username, firstname, lastname, email
			'args': [ validator.StringValidator(3, 64), validator.StringValidator(3, 64), validator.StringValidator(3, 64), validator.EmailValidator() ],
			'callback': createUser
		},
		'--update-user':
		{
			# args: username, firstname, lastname, email
			'args': [ validator.StringValidator(3, 64), validator.StringValidator(3, 64), validator.StringValidator(3, 64), validator.EmailValidator() ],
			'callback': updateUser
		},
		'--show-user':
		{
			# args: username
			'args': [ validator.StringValidator(3, 64) ],
			'callback': showUser
		},
		'--enable-user':
		{
			# args: username
			'args': [ validator.StringValidator(3, 64) ],
			'callback': enableUser
		},
		'--disable-user':
		{
			# args: username
			'args': [ validator.StringValidator(3, 64) ],
			'callback': disableUser
		},
		'--show-users':
		{
			# args: None
			'args': None,
			'callback': showUsers
		}
	   }

# parse arguments & perform requested action:
if __name__ == '__main__':
	cmd = None
	args = []
	action = None

	# test if user has set at least two additional arguments:
	if sys.argv >= 2:
		# check if given action is defined
		if commands.has_key(sys.argv[1]):
			cmd = commands[sys.argv[1]]

	# found defined action...
	if not cmd is None:
		# ...now test if number of arguments is correct:
		if not ((len(sys.argv) - 2 == 0 and cmd['args'] is None) or (cmd['args'] is not None and len(cmd['args']) == len(sys.argv) - 2)):
			print('invalid number of arguments for action "%s"' % sys.argv[1])
			sys.exit(-1)
		else:
			# validate arguments:
			if cmd['args'] is not None:
				for i in range(len(cmd['args'])):
					try:
						cmd['args'][i].validate(sys.argv[i + 2])
						args.append(sys.argv[i + 2])
	
					except Exception, e:
						print('invalid argument at position %d ("%s"): %s' % (i, sys.argv[i + 1], e))
						sys.exit(-1)
			
			action = cmd['callback']

	# execute callback function with validated arguments:
	assert(action is not None)
	action(args)
