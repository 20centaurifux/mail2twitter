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
import tweepy
from encoding import encode

class Twitter:
	def __init__(self, consumer_key=None, consumer_secret=None, access_key=None, access_secret=None):
		self.consumer_key = consumer_key
		self.consumer_secret = consumer_secret
		self.access_key = access_key
		self.access_secret = access_secret

	def getAuthorizationUrl(self):
		return self.__createAuth__().get_authorization_url()

	def getAccessToken(self, pin):
		return self.__createAuth__().get_access_token(pin)

	def publishTweet(self, text):
		self.__createAPI__().update_status(text)

	def followUser(self, username):
		self.__createAPI__().create_friendship(screen_name=username)

	def unfollowUser(self, username):
		self.__createAPI__().destroy_friendship(screen_name=username)

	def __createAuth__(self):
		return tweepy.OAuthHandler(self.consumer_key, self.consumer_secret)

	def __createAPI__(self):
		auth = tweepy.OAuthHandler(self.consumer_key, self.consumer_secret)
		auth.set_access_token(self.access_key, self.access_secret)
		return tweepy.API(auth)
