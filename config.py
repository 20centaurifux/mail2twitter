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

DB_PATH='./'

POP3_SERVER=''
POP3_PORT=110
POP3_USER=''
POP3_PASSWORD=''

SMTP_SERVER=''
SMTP_PORT=25
SMTP_USER=''
SMTP_PASSWORD=''
SMTP_FROM=''

LYNX_EXECUTABLE=''
