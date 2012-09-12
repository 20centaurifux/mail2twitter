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

import time

class MessageGenerator:
	def tweetAccepted(self, text):
		return 'TWEET command accepted: "%s"' % text

	def followAccepted(self, text):
		return 'FOLLOW command accepted: "%s"' % text

	def unfollowAccepted(self, text):
		return 'UNFOLLOW command accepted: "%s"' % text

	def tweetTooShort(self, text):
		return 'TWEET is too short: "%s"' % text

	def tweetTooLong(self, text):
		return 'TWEET is too long: "%s"' % text

	def followNotAccepted(self, text):
		return 'FOLLOW not accepted: %s' % text

	def unfollowNotAccepted(self, text):
		return 'UNFOLLOW not accepted: %s' % text

	def mergeMessages(self, receiver, messages):
		if messages is None:
			text = 'none'
		else:
			text = ''
			sepBegin = '%s BEGIN %s' % ('=' * 40, '=' * 40)
			sepEnd = '%s END %s' % ('=' * 41, '=' * 41)

			for id, msg, timestamp in messages:
				text += '%s\nReceived: %s\n\n%s\n%s\n\n' % (sepBegin, time.ctime(timestamp), msg, sepEnd)

		message =  'Dear %s,\n\nplease find below your latest personal messages:\n\n%s\nKind regards,\n\nYour mail2twitterservice' % (receiver, text)

		return message
