import subprocess

class HtmlRenderer:
	def render(self, html):
		raise Exception('method not implemented')

class LynxRenderer(HtmlRenderer):
	def __init__(self, executable):
		self.__executable = executable

	def render(self, html):
		pipe = subprocess.Popen([self.__executable, '--dump', '--stdin', '--nolist'], shell=False, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
		pipe.stdin.write(html)
		pipe.stdin.close()
		out = pipe.stdout.read().strip()

		return out
