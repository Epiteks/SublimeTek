import sublime
import sublime_plugin
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
			icon = "Packages/Test/" + icons[self.last_pushed_index] + ".png"
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

class	Norme():

	@staticmethod
	def	header(header):
		filename = login = name = "[\s\S]*?"
		line = re.escape("**") + " "
		regex = re.escape("/*") + "\n"
		regex += line + filename + " for [\s\S]*? in [\s\S]*?\n"
		regex += line + "\n"
		regex += line + "Made by " + name + "\n"
		regex += line + "Login   <" + login + "@epitech.net>\n"
		regex += line + "\n"
		regex += line + "Started on\t[\s\S]*?" + name + "\n"
		regex += line + "Last update\t[\s\S]*?" + name + "\n"
		regex += re.escape("*/") + "\n"
		headerInline = ""
		for line in header.lines:
			headerInline += line.text + "\n"
		pattern = re.compile(regex)
		if not pattern.match(headerInline):
			header.errors.append(Error("BADHEAD", "", "HEAD"))

	@staticmethod
	def	includes(includes):
		sys = True
		sys_regex = re.compile("#\s*include\s*<[\s\S]+?>")
		usr_regex = re.compile("#\s*include\s*\"[\s\S]+?\"")
		for include in includes.lines:
			if sys_regex.match(include.text):
				if not sys:
					include.errors.append(Error("WRGLOCINCL", include.text, "INC", include))
			elif usr_regex.match(include.text):
				if sys:
					sys = False

	@staticmethod
	def	columns(line):
		rawLine = line.text.replace("\t", "      ")
		if len(rawLine) > 80:
			line.errors.append(Error("NBCOL", rawLine[80:], "LINE", line))

	@staticmethod
	def	keyword(line):
		regex = re.compile("(\sif\s?)+|(\swhile\s?)+|(\sreturn\s?)+")
		regex_space = re.compile("(\sif\s)+|(\swhile\s)+|(\sreturn\s)+")
		res = regex.match(line.text)
		if res:
			res_text = res.group(0)
			last_res = regex_space.match(res_text)
			if not last_res:
				line.errors.append(Error("NOSPCKEY", res_text, "LINE", line))
		return

	@staticmethod
	def	line(line):
		Norme.columns(line)
		Norme.keyword(line)

	@staticmethod
	def	function(function):
		inside_func = False
		count_lines = 0
		for line in function.lines:
			if line.text == "{":
				inside_func = True
			elif line.text == "}":
				inside_func = False
			elif inside_func:
				count_lines += 1
			Norme.line(line)
		if count_lines > 25:
			function.errors.append(Error("NBFUNCLNS", "", "FUNC"))

class	EpitechNormeCommand(sublime_plugin.TextCommand):

	def	get_syntax(self):
		rawSyntax = self.view.settings().get("syntax")
		rawTab = rawSyntax.split("/")
		if (len(rawTab)):
			rawSubTab = rawTab[(len(rawTab) - 1)].split(".")
			if (len(rawSubTab)):
				rawSecondSubTab = rawSubTab[0].split(" ")
				if (len(rawSecondSubTab)):
					language = rawSecondSubTab[0];
					return language
		return rawSyntax

	def	get_file(self):
		region = sublime.Region(0, self.view.size())
		text = self.view.substr(region)
		file = File(text)
		return file

	def	highlight(self, file, errors):
		items = errors.get_next_list()
		while items != None:
			key, icon = errors.get_current_infos()
			self.view.erase_regions(key)
			regions = []
			for item in items:
				if item.line:
					start = item.line.start
					end = start + len(item.line.text)
					if item.code == ErrorCode.value("NBCOL") and item.text:
						start = end - len(item.text)
					if item.code == ErrorCode.value("NBNEWLINE"):
						end += 1
				elif item.code == ErrorCode.value("NOHEAD") or item.code == ErrorCode.value("BADHEAD"):
					start = 0
					end = start
					for line in file.header.lines:
						end += len(line.text) + 1
				elif item.code == ErrorCode.value("NBFUNCS"):
					count = 0
					start = -1
					for func in file.functions:
						if func.type == "FUNC":
							count += 1
						if count > 5:
							if start == -1:
								start = func.lines[0].start
								end = start
							for line in func.lines:
								end += len(line.text) + 1
				regions.append(sublime.Region(start, end))
			self.view.add_regions(key, regions, "support", icon)
			items = errors.get_next_list()

	def	test(self, val):
		print (val)

	def	pop_errors(self, errors):
		return

	def	show_errors(self, file):
		errors = Highlight()
		for error in file.errors:
			errors.add(error)
		for error in file.header.errors:
			errors.add(error)
		for error in file.includes.errors:
			errors.add(error)
		for line in file.includes.lines:
			for error in line.errors:
				errors.add(error)
		for function in file.functions:
			for error in function.errors:
				errors.add(error)
			for line in function.lines:
				for error in line.errors:
					errors.add(error)
		self.highlight(file, errors)
		self.pop_errors(errors.to_string())

	def	execute(self, edit, file):
		Norme.header(file.header)
		Norme.includes(file.includes)
		if len(file.functions) > 5:
			file.errors.append(Error("NBFUNCS", "", "FILE"))
		for function in file.functions:
			Norme.function(function)
		self.show_errors(file)

	def	run(self, edit):
		syntax = self.get_syntax()
		if syntax != "C":
			return
		file = self.get_file()
		self.execute(edit, file)
