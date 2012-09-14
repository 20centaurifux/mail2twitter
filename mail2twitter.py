"""
	project............: mail2twitter
	version............: 0.1
	date...............: 09/12
	copyright..........: Sebastian Fedrau
	email..............: lord-kefir@arcor.de

	Permission is hereby granted, free of charge, to any person obtaining
	a copy of this software and associated documentation files (the
	"Software"), to deal in the Software without restriction, including
	without limitation the rights to use, copy, modify, merge, publish,
	distribute, sublicense, and/or sell copies of the Software, and to
	permit persons to whom the Software is furnished to do so, subject to
	the following conditions:

	The above copyright notice and this permission notice shall be
	included in all copies or substantial portions of the Software.

	THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
	EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
	MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
	IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR
	OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
	ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
	OTHER DEALINGS IN THE SOFTWARE.

	This synchronziation procedure works only file-based. It will not upload
	empty folders or remove empty folders on the remote site.
"""

# -*- coding: utf-8 -*-
import database, mail, validator, config, htmlrenderer, messagegenerator, twitter
import sys, re, time, email.utils
from quopri import decodestring
from encoding import encode

# helpers:
def connectToDatabase():
	return database.Database(config.DB_PATH)

def createMailer():
	return mail.Mail(config.POP3_SERVER, config.POP3_PORT, config.POP3_USER, config.POP3_PASSWORD, \
		config.SMTP_SERVER, config.SMTP_PORT, config.SMTP_USER, config.SMTP_PASSWORD, config.SMTP_FROM)

def createHtmlRenderer():
	return htmlrenderer.LynxRenderer(config.LYNX_EXECUTABLE)

def createMessageGenerator():
	return messagegenerator.MessageGenerator()

def createTwitterClient():
	# try to get access key & secret from database:
	db = connectToDatabase()
	key, secret = db.getOAuthData()

	return twitter.Twitter(config.CONSUMER_KEY, config.CONSUMER_SECRET, key, secret)

def convertTypeToText(typeId):
	if typeId == database.PUBLISH_TWEET:
		return 'TWEET'
	elif typeId == database.FOLLOW_USER:
		return 'FOLLOW'
	elif typeId == database.UNFOLLOW_USER:
		return 'UNFOLLOW'

	return None

# actions:
def createUser(args):
	username, firstname, lastname, email = args

	db = connectToDatabase()

	if not db.userExists(username):
		db.createUser(username, firstname, lastname, email)
	else:
		raise Exception('given username does already exist')

def updateUser(args):
	username, firstname, lastname, email = args

	db = connectToDatabase()

	if db.userExists(username):
		db.updateUser(username, firstname, lastname, email)
	else:
		raise Exception('couldn\'t find user: "%s"' % username)

def showUser(args):
	username = args[0]

	db = connectToDatabase()

	if db.userExists(username):
		firstname, lastname, email, blocked = db.getUser(username)
		print 'user........: %s\nfirstname...: %s\nlastname....: %s\nemail.......: %s\nblocked.....: %d' % (username, firstname, lastname, email, blocked)
	else:
		raise Exception('couldn\'t find user: "%s"' % username)

def enableUser(args):
	username = args[0]

	db = connectToDatabase()
	db.blockUser(username, 0)

def disableUser(args):
	username = args[0]

	db = connectToDatabase()
	db.blockUser(username, 1)

def showUsers(args):
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

def showQueue(args):
	db = connectToDatabase()

	for id, username, email, typeId, text, timestamp in db.getQueue():
		print('%d. %s %s: "%s", %s<%s>' % (id, time.ctime(timestamp), convertTypeToText(typeId), text, username, email))

def showHistory(args):
	db = connectToDatabase()

	for id, username, email, typeId, text, timestamp in db.getHistory():
		print('%d. %s %s: "%s", %s<%s>' % (id, time.ctime(timestamp), convertTypeToText(typeId), text, username, email))

def deleteFromQueue(args):
	id = args[0]

	db = connectToDatabase()
	db.deleteFromQueue(id)

def clearQueue(args):
	db = connectToDatabase()
	db.deleteQueue()

def fetchMails(args):
	# fetch emails:
	m = createMailer()
	mails = m.fetchMails()

	# connect to database & get enabled email addresses:
	db = connectToDatabase()
	addresses = db.getEnabledAddresses()

	# create message generator:
	messages = createMessageGenerator()

	# check received mails:
	for mail in mails:
		# validate sender:
		fromAddr = email.utils.parseaddr(mail['From'])
		sender = fromAddr[1].strip().lower()

		if sender in addresses:
			# parse email:
			subject = mail['Subject'].lower().strip()

			if subject == 'tweet':
				action = database.PUBLISH_TWEET
			elif subject == 'follow':
				action = database.FOLLOW_USER
			elif subject == 'unfollow':
				action = database.UNFOLLOW_USER
			else:
				action = -1

			if action <> -1:
				date = time.mktime(email.utils.parsedate(mail['Date']))

				if mail.is_multipart():
					body = mail.get_payload(0).get_payload().strip()
				else:
					body = mail.get_payload().strip()

				body = encode(decodestring(body))

				m = re.match('^<html>.*', body)

				if not m is None:
					r = createHtmlRenderer()
					body = r.render(body)

				# validate body & append message to queue on success:
				if action == database.PUBLISH_TWEET:
					if len(body) < 5:
						db.createMessage(addresses[sender], messages.tweetTooShort(body))
					elif len(body) > 140:
						db.createMessage(addresses[sender], messages.tweetTooLong(body))
					else:
						db.createMessage(addresses[sender], messages.tweetAccepted(body))
						db.appendToQueue(addresses[sender], action, body, date, time.time())
				else:
					for username in [u.strip() for u in body.split(',')]:
						if len(username) < 3 or len(username) > 24:
							if action == database.FOLLOW_USER:
								db.createMessage(addresses[sender], messages.followNotAccepted(body))
							else:
								db.createMessage(addresses[sender], messages.unfollowNotAccepted(body))
						else:
							if action == database.FOLLOW_USER:
								db.createMessage(addresses[sender], messages.followAccepted(username))
							else:
								db.createMessage(addresses[sender], messages.unfollowAccepted(username));
	
							db.appendToQueue(addresses[sender], action, body, date, time.time())

def showMessageQueue(args):
	db = connectToDatabase()

	for id, username, email, text, timestamp in db.getMessageQueue():
		print('%d. %s to %s<%s>: "%s"' % (id, time.ctime(timestamp), username, email, text))

def deleteFromMessageQueue(args):
	id = args[0]

	db = connectToDatabase()
	db.deleteFromMessageQueue(id)

def clearMessageQueue(args):
	db = connectToDatabase()
	db.deleteMessageQueue()

def showSentLog(args):
	db = connectToDatabase()

	for username, email, text, sentDate in db.getSentLog():
		print('%s to %s<%s>: "%s"' % (time.ctime(sentDate), username, email, text))

def sendMessages(args):
	generator = createMessageGenerator()
	db = connectToDatabase()
	mail = createMailer()

	for id, username, email, firstname, lastname in db.getReceivers():
		messages = db.getMessagesFromUser(id)

		fullMessage = generator.mergeMessages(firstname, messages)
		mail.sendMail(email, 'Your latest messages', fullMessage)
		db.markMessagesSent([r[0] for r in messages])

def authenticate(args):
	# get authentication url:
	twitter = createTwitterClient()

	url = twitter.getAuthorizationUrl()
	print('Please visit the following id to request a PIN: %s' % url)

	# read pin:
	pin = raw_input('PIN: ').strip()

	# get access key/secret from Twitter:
	key, secret = twitter.getAccessToken(pin)

	# store key/secret in database:
	db = connectToDatabase()
	db.saveOAuthData(key, secret)

def post(args):
	userIds = {}
	db = connectToDatabase()
	twitter = createTwitterClient()
	generator = createMessageGenerator()

	# get commands from queue:
	for id, username, email, typeId, text, timestamp in db.getQueue():
		if not username in userIds:
			userIds[username] = db.mapUser(username)

		# post to Twitter:
		try:
			if typeId == database.PUBLISH_TWEET:
				twitter.publishTweet(text)
				db.createMessage(userIds[username], generator.tweetPublished(text))
			elif typeId == database.FOLLOW_USER or typeId == database.UNFOLLOW_USER:
				for user in [u.strip() for u in text.split(',')]:
					if typeId == database.FOLLOW_USER:
						twitter.followUser(user)
						db.createMessage(userIds[username], generator.followingUser(user))
					else:
						twitter.unfollowUser(user)
						db.createMessage(userIds[username], generator.unfollowingUser(user))

			# move queue item to history
			db.moveQueueItemToHistory(id)

		except Exception, e:
			db.createMessage(userIds[username], generator.failureOccured(e) + ' (queueId=%d)' % id)

# usage:
def printUsage(args=None):
	print('USAGE: mail2twitter.py --[command] [arg1] [arg2] ...\n')
	print('The following commands are available:')
	print('\tTWITTER')
	print('\t--authenticate                    grant access to your account to mail2twitter')
	print('\t--post                            process queue and post to Twitter\n')
	print('\tUSER DATABASE')
	print('\t--create-user [username] [firstname] [lastname] [email]   add user to user database')
	print('\t--update-user [username] [firstname] [lastname] [email]   update an existing user')
	print('\t--enable-user [username]                                  enable user account')
	print('\t--disable-user [username]                                 disable user account')
	print('\t--show-users                                              print all users from the user database')
	print('\t--show-user [username]                                    print details of a user\n')
	print('\tQUEUE')
	print('\t--show-queue                      print current queue')
	print('\t--delete-from-queue [id]          delete item from the queue')
	print('\t--clear-queue                     delete all items from the queue')
	print('\t--show-history                    print history\n')
	print('\tMESSAGES')
	print('\t--show-message-queue              print current message queue')
	print('\t--delete-from-message-queue [id]  delete item from the message queue')
	print('\t--clear-message-queue             delete all items from the message queue')
	print('\t--send-messages                   send messages from message queue (SMTP)')
	print('\t--show-sent-log                   show sent messages\n')
	print('\tPOP3')
	print('\t--fetch-mails                     receive mails from specified POP3 account\n')
	print('\tGENERAL')
	print('\t--help                            show this text\n')

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
			'args': None,
			'callback': showUsers
		},
		'--show-queue':
		{
			'args': None,
			'callback': showQueue
		},
		'--show-history':
		{
			'args': None,
			'callback': showHistory
		},
		'--delete-from-queue':
		{
			# args: id
			'args': [ validator.NumberValidator(0) ],
			'callback': deleteFromQueue
		},
		'--clear-queue':
		{
			'args': None,
			'callback': clearQueue
		},
		'--fetch-mails':
		{
			'args': None,
			'callback': fetchMails
		},
		'--show-message-queue':
		{
			'args': None,
			'callback': showMessageQueue
		},
		'--delete-from-message-queue':
		{
			# args: id
			'args': [ validator.NumberValidator(0) ],
			'callback': deleteFromMessageQueue
		},
		'--clear-message-queue':
		{
			'args': None,
			'callback': clearMessageQueue
		},
		'--show-sent-log':
		{
			'args': None,
			'callback': showSentLog
		},
		'--send-messages':
		{
			'args': None,
			'callback': sendMessages
		},
		'--authenticate':
		{
			'args': None,
			'callback': authenticate
		},
		'--post':
		{
			'args': None,
			'callback': post
		},
		'--help':
		{
			'args': None,
			'callback': printUsage
		}
	   }

# parse arguments & perform requested action:
if __name__ == '__main__':
	cmd = None
	args = []
	action = None

	t = createTwitterClient()

	# test if user has set at least two additional arguments:
	if len(sys.argv) >= 2:
		# check if given action is defined
		if commands.has_key(sys.argv[1]):
			cmd = commands[sys.argv[1]]
	else:
		printUsage()

	if cmd is None:
		printUsage()
		sys.exit(-1)

	# test if number of arguments is correct:
	if not ((len(sys.argv) - 2 == 0 and cmd['args'] is None) or (cmd['args'] is not None and len(cmd['args']) == len(sys.argv) - 2)):
		print('invalid number of arguments for action "%s"' % sys.argv[1])
		sys.exit(-1)
	else:
		# validate arguments:
		if cmd['args'] is not None:
			for i in range(len(cmd['args'])):
				try:
					cmd['args'][i].validate(sys.argv[i + 2])
					args.append(sys.argv[i + 2].rstrip('\n'))

				except Exception, e:
					print('invalid argument at position %d ("%s"): %s' % (i + 1, sys.argv[i + 2], e))
					sys.exit(-1)

		action = cmd['callback']

	# execute callback function with validated arguments:
	assert(action is not None)

	try:
		action(args)

	except Exception, e:
		print e
		sys.exit(-1)
