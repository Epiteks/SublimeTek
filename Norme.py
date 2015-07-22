import sublime
import sublime_plugin
import re

if not int(sublime.version()) >= 3000:
	import Parse
else:
	from . import Parse

class	Norme():

	@staticmethod
	def	header(header):
		lines = []
		filename = login = name = "[\s\S]*?"
		line = re.escape("**") + " "
		lines.append(re.escape("/*"))
		lines.append(line + filename + " for [\s\S]*? in [\s\S]*?")
		lines.append(line)
		lines.append(line + "Made by " + name)
		lines.append(line + "Login   <" + login + "@epitech.net>")
		lines.append(line)
		lines.append(line + "Started on\t[\s\S]*?" + name)
		lines.append(line + "Last update\t[\s\S]*?" + name)
		lines.append(re.escape("*/"))
		for user, head in zip(header.lines, lines):
			pattern = re.compile(head)
			if not pattern.match(user.text):
				user.errors.append(Parse.Error("BADHEAD", user.text, "HEAD", user))

	@staticmethod
	def	includes(includes):
		sys = True
		sys_regex = re.compile("#\s*include\s*<[\s\S]+?>")
		usr_regex = re.compile("#\s*include\s*\"[\s\S]+?\"")
		for include in includes.lines:
			if sys_regex.match(include.text):
				if not sys:
					include.errors.append(Parse.Error("WRGLOCINCL", include.text, "INC", include))
			elif usr_regex.match(include.text):
				if sys:
					sys = False

	@staticmethod
	def	columns(line):
		rawLine = line.text.replace("\t", "      ")
		if len(rawLine) > 80:
			line.errors.append(Parse.Error("NBCOL", rawLine[80:], "LINE", line))

	@staticmethod
	def	keyword(line):
		regex = re.compile("(\sif\s?)+|(\swhile\s?)+|(\sreturn\s?)+")
		regex_space = re.compile("(\sif\s)+|(\swhile\s)+|(\sreturn\s)+")
		res = regex.match(line.text)
		if res:
			res_text = res.group(0)
			last_res = regex_space.match(res_text)
			if not last_res:
				line.errors.append(Parse.Error("NOSPCKEY", res_text, "LINE", line))
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
			function.errors.append(Parse.Error("NBFUNCLNS", "", "FUNC"))

class	SublimeTekNormeCommand(sublime_plugin.TextCommand):

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
		file = Parse.File(text)
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
					if item.code == Parse.ErrorCode.value("NBCOL") and item.text:
						start = end - len(item.text)
					if item.code == Parse.ErrorCode.value("NBNEWLINE"):
						end += 1
				elif item.code == Parse.ErrorCode.value("NOHEAD"):
					start = 0
					end = start
					for line in file.header.lines:
						end += len(line.text) + 1
				elif item.code == Parse.ErrorCode.value("NBFUNCS"):
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

	def	pop_errors(self, errors):
		return

	def	show_errors(self, file):
		errors = Parse.Highlight()
		for error in file.errors:
			errors.add(error)
		for error in file.header.errors:
			errors.add(error)
		for line in file.header.lines:
			for error in line.errors:
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
			file.errors.append(Parse.Error("NBFUNCS", "", "FILE"))
		for function in file.functions:
			Norme.function(function)
		self.show_errors(file)

	def	run(self, edit):
		syntax = self.get_syntax()
		if syntax != "C":
			return
		file = self.get_file()
		self.execute(edit, file)
