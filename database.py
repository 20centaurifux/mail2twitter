import sqlite3, os

PUBLISH_TWEET = 0
FOLLOW_USER   = 1
UNFOLLOW_USER = 2

class Database:
	def __init__(self, directory):
		filename = os.path.join(directory, 'mail2twitter.db')
		self.__connection = sqlite3.connect(filename, isolation_level=None)
		self.__connection.text_factory = lambda t: unicode(t, "utf-8", "ignore")
		self.__cursor = self.__connection.cursor()
		self.__createTables__()

	def userExists(self, username):
		self.__cursor.execute('SELECT COUNT(*) FROM User WHERE Username=?', (username, ))

		if int(self.__cursor.fetchone()[0]) == 0:
			return False

		return True

	def createUser(self, username, firstname, lastname, email):
		self.__cursor.execute('INSERT INTO User (Username, Firstname, Lastname, Email, Blocked) VALUES (?, ?, ?, ?, 0)', (username, firstname, lastname, email))

	def updateUser(self, username, firstname, lastname, email):
		self.__cursor.execute('UPDATE User SET Firstname=?, Lastname=?, Email=? WHERE username=?', (firstname, lastname, email, username))

	def getUser(self, username):
		self.__cursor.execute('SELECT Firstname, Lastname, Email, Blocked FROM User WHERE Username=?', (username, ))

		return self.__cursor.fetchone()

	def blockUser(self, username, blocked):
		self.__cursor.execute('UPDATE User SET blocked=? WHERE Username=?', (blocked, username))

	def userIsBlocked(self, username):
		self.__cursor.execute('SELECT Blocked FROM User WHERE Username=?', (username, ))

		if int(self.__cursor.fetchone()[0]) == 0:
			return False

		return True

	def getUsers(self):
		users = []

		self.__cursor.execute('SELECT Username, Email, Blocked FROM User ORDER BY Username')

		for row in self.__cursor.fetchall():
			users.append(row)

		return users

	def mapUser(self, username):
		self.__cursor.execute('SELECT ID, Firstname, Lastname, Email, Blocked FROM User WHERE Username=?', (username, ))

		result = self.__cursor.fetchone()

		if not result is None:
			return int(result[0])

		return None

	def appendToQueue(self, userId, typeId, text, ctime):
		self.__cursor.execute('INSERT INTO Queue (UserId, TypeId, Text, CTime) VALUES (?, ?, ?, ?)', (userId, typeId, text, ctime))

	def getQueue(self):
		items = []

		self.__cursor.execute('SELECT Queue.ID, username, email, TypeID, Text, CTime FROM Queue INNER JOIN User ON UserID=User.ID ORDER BY CTime')

		for row in self.__cursor.fetchall():
			items.append(row)

		return items

	def __createTables__(self):
		self.__cursor.execute('CREATE TABLE IF NOT EXISTS User (ID INT PRIMARY KEY, Username VARCHAR(64) UNIQUE, Firstname VARCHAR(64) NOT NULL, ' \
			'Lastname VARCHAR(64) NOT NULL, Email VARCHAR(64) NOT NULL UNIQUE, Blocked BIT NOT NULL)')
