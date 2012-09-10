import sqlite3, os

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

		row = self.__cursor.fetchone()

		return row

	def blockUser(self, username, blocked):
		self.__cursor.execute('UPDATE User SET blocked=? WHERE Username=?', (blocked, username))

	def getUsers(self):
		users = []

		self.__cursor.execute('SELECT Username, Email, Blocked FROM User ORDER BY Username')

		for row in self.__cursor.fetchall():
			users.append(row)

		return users

	def __createTables__(self):
		self.__cursor.execute('CREATE TABLE IF NOT EXISTS User (ID INT PRIMARY KEY, Username VARCHAR(64) UNIQUE, Firstname VARCHAR(64) NOT NULL, ' \
			'Lastname VARCHAR(64) NOT NULL, Email VARCHAR(64) NOT NULL UNIQUE, Blocked BIT NOT NULL)')
