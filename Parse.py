import re

class	ErrorCode:

	@staticmethod
	def	get_tabs():
		codes = ["NOHEAD", "BADHEAD", "WRGLOCINCL", "NBCOL", "NOSPCKEY", "NBFUNCLNS", "NBFUNCS", "NBNEWLINE"]
		icons = ["head", "head", "include", "columns", "space", "lines", "function", "newline"]
		texts = ["No Header", "Invalid Header", "Bad Include Order", "More Than 80 Columns", "Missing Space After Keyword", "More Than 25 Lines", "More Than 5 Functions", "More Than 1 Consecutive \n"]
		return codes, icons, texts

	@staticmethod
	def	value(code):
		codes, icons, texts = ErrorCode.get_tabs()
		if not code in codes:
			return -1
		return codes.index(code)

	@staticmethod
	def	code(value):
		codes, icons, texts = ErrorCode.get_tabs()
		if value < 0 or value >= len(codes):
			return -1
		return codes[value]

	@staticmethod
	def	icon(value):
		codes, icons, texts = ErrorCode.get_tabs()
		if value < 0 or value >= len(icons):
			return -1
		return icons[value]

	@staticmethod
	def	text(value):
		codes, icons, texts = ErrorCode.get_tabs()
		if value < 0 or value >= len(texts):
			return -1
		return texts[value]

class	Highlight():

	def	__init__(self):
		self.last_pushed_index = -1
		self.errors = []
		codes, icons, texts = ErrorCode.get_tabs()
		for code in codes:
			sub_list = []
			self.errors.append(sub_list)

	def	add(self, error):
		if error.code != -1:
			self.errors[error.code].append(error)

	def	show(self):
		for items in self.errors:
			for item in items:
				if item.line:
					print("(" + str(item.code) + ")" + item.block + ":" + item.line.text + "/" + item.text)
				else:
					print("(" + str(item.code) + ")" + item.block)

	def	get_next_list(self):
		self.last_pushed_index += 1
		if self.last_pushed_index < len(self.errors):
			current = self.errors[self.last_pushed_index]
			return current
		else:
			return None

	def	get_current_infos(self):
		codes, icons, texts = ErrorCode.get_tabs()
		if self.last_pushed_index < len(self.errors):
			icon = "Packages/Sublime-Tek/icons/" + icons[self.last_pushed_index]
			return codes[self.last_pushed_index], icon
		else:
			return None, None

	def	to_string(self):
		strings = []
		for items in self.errors:
			for item in items:
				strings.append(item.to_string())
		return strings

class	Error():

	def	__init__(self, code, text, block = None, line = None):
		self.code = ErrorCode.value(code)
		self.text = text
		self.block = block
		self.line = line

	def	to_string(self):
		string = ""
		if self.line:
			string += "Line " + str(self.line.pos) + " : "
		string += ErrorCode.text(self.code)
		return string

class	Line():

	def	__init__(self, nb, start, text):
		self.pos = nb
		self.start = start
		self.text = text
		self.errors = []

class	Block():

	def	__init__(self, type):
		self.type = type
		self.lines = []
		self.errors = []

class	File():

	def	__init__(self, text):
		self.text = text
		self.raw = []
		self.lines = []
		self.header = Block("HEAD")
		self.includes = Block("INC")
		self.functions = []
		self.errors = []
		self.parse_lines()

	def	get_blocks(self):
		pos = 0
		prototype = re.compile("([a-zA-Z0-9_\-]+\*?[\t ]+)+[a-zA-Z0-9_\-*]+?\([\s\S]*?\)")
		already_inc = False
		new_line = False
		empty = None
		while pos < len(self.lines):
			tmp = self.lines[pos].text
			if tmp == "":
				if not empty:
					empty = Block("EMPTY")
				if new_line:
					self.lines[pos].errors.append(Error("NBNEWLINE", "", "FILE", self.lines[pos]))
				empty.lines.append(self.lines[pos])
				new_line = True
			else:
				new_line = False
				if empty:
					self.functions.append(empty)
					empty = None
				if not already_inc and tmp.startswith("#include"):
					while self.lines[pos].text.startswith("#include"):
						self.includes.lines.append(self.lines[pos])
						pos += 1
					pos -= 1
				elif prototype.match(tmp):
					function = Block("FUNC")
					while self.lines[pos].text != "}":
						function.lines.append(self.lines[pos])
						pos += 1
					function.lines.append(self.lines[pos])
					self.functions.append(function)
			pos += 1

	def	parse_lines(self):
		self.raw = self.text.split("\n")
		start = 0
		index = 1
		if len(self.raw) < 9:
			self.error = Error("NOHEAD", "", "HEAD")
			return
		for line in self.raw[0:9]:
			tmp = line.replace("\n", "")
			self.header.lines.append(Line(index, start, tmp))
			start += len(line) + 1
			index += 1
		for line in self.raw[9:]:
			tmp = line.replace("\n", "")
			self.lines.append(Line(index, start, tmp))
			start += len(line) + 1
			index += 1
		self.get_blocks()
