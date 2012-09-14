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
import poplib, smtplib, email, string
from email.mime.text import MIMEText
from encoding import encode

class Mail:
	def __init__(self, pop3Server, pop3Port, pop3User, pop3Password, smtpServer, smtpPort, smtpUser, smtpPassword, smtpFrom):
		self.__pop3Server = pop3Server
		self.__pop3Port = pop3Port
		self.__pop3User = pop3User
		self.__pop3Password = pop3Password
		self.__smtpServer = smtpServer
		self.__smtpPort = smtpPort
		self.__smtpUser = smtpUser
		self.__smtpPassword = smtpPassword
		self.__smtpFrom = smtpFrom

	def fetchMails(self):
		mails = []

		# connect to pop3 server:
		client = poplib.POP3(self.__pop3Server, self.__pop3Port)
		client.user(self.__pop3User)
		client.pass_(self.__pop3Password)

		# receive messages:
		numMessages = len(client.list()[1])

		for i in range(numMessages):
			msg = client.retr(i + 1)
			str = string.join(msg[1], '\n')

			mails.append(email.message_from_string(str))

		# delete messages:
		for i in range(numMessages):
			client.dele(i + 1)

		client.quit()

		return mails

	def sendMail(self, receiver, subject, text):
		msg = MIMEText(text, 'plain', 'utf-8')

		msg['Subject'] = subject
		msg['From'] = self.__smtpFrom
		msg['To'] = receiver

		client = smtplib.SMTP()
		client.connect(self.__smtpServer, self.__smtpPort)
		client.login(self.__smtpUser, self.__smtpPassword)
		client.sendmail(self.__smtpFrom, [receiver], msg.as_string())
		client.quit()
