import poplib, email, string
import sys

class Mail:
	def __init__(self, pop3Server, pop3Port, pop3User, pop3Password):
		self.__pop3Server = pop3Server
		self.__pop3Port = pop3Port
		self.__pop3User = pop3User
		self.__pop3Password = pop3Password

	def fetchMails(self):
		mails = []

		client = poplib.POP3(self.__pop3Server, self.__pop3Port)
		client.user(self.__pop3User)
		client.pass_(self.__pop3Password)

		numMessages = len(client.list()[1])

		for i in range(numMessages):
			msg = client.retr(i + 1)
			str = string.join(msg[1], '\n')

			mails.append(email.message_from_string(str))

		client.quit()

		return mails
