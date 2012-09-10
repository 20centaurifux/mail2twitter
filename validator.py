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
