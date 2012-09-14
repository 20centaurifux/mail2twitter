"""
	file...............: mail2twitter.py
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
import re

class Validator:
	def validate(self, value):
		raise Exception('method not implemented')

class StringValidator(Validator):
	def __init__(self, min, max):
		self.__min = min
		self.__max = max

	def validate(self, value):
		if value is None and self.__min <> 0:
			raise Exception('the entered value is too short')

		if len(value) < self.__min:
			raise Exception('the entered value is too short')

		if len(value) > self.__max:
			raise Exception('the entered value is too long')

class EmailValidator(Validator):
	def validate(self, value):
		if re.match('^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$', value) is None:
			raise Exception('there entered text is no valid email address')

class NumberValidator(Validator):
	def __init__(self, min=None, max=None):
		self.__min = min
		self.__max = max

	def validate(self, value):
		n = int(value)

		if not self.__min is None and n < self.__min:
				raise Exception('the entered value exceeds the minimum')

		if not self.__max is None and n < self.__max:
				raise Exception('the entered value exceeds the maximum')
