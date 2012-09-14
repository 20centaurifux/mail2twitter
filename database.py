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
import sqlite3, os, time, string

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
		self.__cursor.execute('SELECT Username, Email, Blocked FROM User ORDER BY Username')

		return self.__cursor.fetchall()

	def mapUser(self, username):
		self.__cursor.execute('SELECT ID, Firstname, Lastname, Email, Blocked FROM User WHERE Username=?', (username, ))

		result = self.__cursor.fetchone()

		if not result is None:
			return int(result[0])

		return None

	def getEnabledAddresses(self):
		addresses = {}

		self.__cursor.execute('SELECT ID, Email FROM User WHERE Blocked=0 ORDER BY Email')

		for id, email in self.__cursor.fetchall():
			addresses[email] = id

		return addresses

	def appendToQueue(self, userId, typeId, text, received, timestamp):
		self.__cursor.execute('INSERT INTO Queue (UserId, TypeId, Text, Received, Timestamp) VALUES (?, ?, ?, ?, ?)', (userId, typeId, text, received, timestamp))

	def deleteFromQueue(self, id):
		self.__cursor.execute('DELETE FROM Queue WHERE ID=?', (id, ))

	def deleteQueue(self):
		self.__cursor.execute('DELETE FROM Queue')

	def getQueue(self):
		self.__cursor.execute('SELECT Queue.ID, Username, Email, TypeID, Text, Received FROM Queue INNER JOIN User ON UserID=User.ID ORDER BY Timestamp')

		return self.__cursor.fetchall()

	def moveFromQueueToHistory(self, id):
		# get queue item:
		self.__cursor.execute('SELECT UserID, TypeID, Text, Received FROM Queue WHERE ID=?', (id, ))
		userId, typeId, text, received = self.__cursor.fetchone()

		# insert history record:
		self.__cursor.execute('INSERT INTO History (UserID, TypeID, Text, Received, Timestamp) VALUES (?, ?, ?, ?, ?)', \
			(userId, typeId, text, received, time.time()))

		# delete queue item:
		self.__cursor.execute('DELETE FROM Queue WHERE ID=?', (id, ))

	def getHistory(self):
		self.__cursor.execute('SELECT History.ID, Username, Email, TypeID, Text, Timestamp FROM History INNER JOIN User ON UserID=User.ID ORDER BY Timestamp')

		return self.__cursor.fetchall()

	def createMessage(self, receiverId, text):
		self.__cursor.execute('INSERT INTO Message (ReceiverID, Text, Timestamp, Sent, SentDate) VALUES (?, ?, ?, 0, NULL)', (receiverId, text, time.time()))

	def getMessageQueue(self):
		self.__cursor.execute('SELECT Message.ID, Username, Email, Text, Timestamp FROM Message INNER JOIN User ON ReceiverID=User.ID AND Blocked=0 AND Sent=0 ORDER BY Timestamp')

		return self.__cursor.fetchall()

	def deleteFromMessageQueue(self, id):
		self.__cursor.execute('DELETE FROM Message WHERE ID=?', (id, ))

	def deleteMessageQueue(self):
		self.__cursor.execute('DELETE FROM Message')

	def getSentLog(self):
		self.__cursor.execute('SELECT Username, Email, Text, SentDate FROM Message INNER JOIN User ON ReceiverID=User.ID AND Blocked=0 AND Sent=1 ORDER BY SentDate DESC')

		return self.__cursor.fetchall()

	def getReceivers(self):
		self.__cursor.execute('SELECT DISTINCT(ReceiverID), Username, Email, Firstname, Lastname FROM Message INNER JOIN User ON User.ID=ReceiverID WHERE Blocked=0 ORDER BY ReceiverID')

		return self.__cursor.fetchall()

	def getMessagesFromUser(self, userId):
		self.__cursor.execute('SELECT ID, Text, Timestamp FROM Message WHERE ReceiverID=? ORDER BY Timestamp', (userId, ))

		return self.__cursor.fetchall()

	def markMessagesSent(self, messageIds):
		self.__cursor.execute('UPDATE Message SET Sent=1, SentDate=? WHERE ID IN (%s)' %  string.join([str(id) for id in messageIds], ','), (time.time(), ))

	def saveOAuthData(self, access_key, access_secret):
		self.__cursor.execute('DELETE FROM OAuth')
		self.__cursor.execute('INSERT INTO OAuth (Key, Secret) VALUES (?, ?)', (access_key, access_secret))

	def getOAuthData(self):
		self.__cursor.execute('SELECT Key, Secret FROM OAuth')

		row = self.__cursor.fetchone()

		if not row is None:
			return row

		return [None, None]

	def __createTables__(self):
		self.__cursor.execute('CREATE TABLE IF NOT EXISTS User (ID INTEGER PRIMARY KEY NOT NULL, Username VARCHAR(64) UNIQUE, Firstname VARCHAR(64) NOT NULL, ' \
			'Lastname VARCHAR(64) NOT NULL, Email VARCHAR(64) NOT NULL UNIQUE, Blocked BIT NOT NULL)')

		self.__cursor.execute('CREATE TABLE IF NOT EXISTS Queue (ID INTEGER PRIMARY KEY, UserID INT NOT NULL, TypeID INT NOT NULL, Text VARCHAR(256) NOT NULL, ' \
			'Received INT NOT NULL, Timestamp INT NOT NULL)')

		self.__cursor.execute('CREATE TABLE IF NOT EXISTS History (ID INTEGER PRIMARY KEY, UserID INT NOT NULL, TypeID INT NOT NULL, Text VARCHAR(256) NOT NULL, ' \
			'Received INT NOT NULL, Timestamp INT NOT NULL)')

		self.__cursor.execute('CREATE TABLE IF NOT EXISTS Message (ID INTEGER PRIMARY KEY, ReceiverID INT NOT NULL, Text VARCHAR(2048) NOT NULL, ' \
			'Timestamp INT NOT NULL, Sent BIT NOT NULL, SentDate INT)')

		self.__cursor.execute('CREATE TABLE IF NOT EXISTS OAuth (Key VARCHAR(64) NOT NULL, Secret VARCHAR(64) NOT NULL)')
