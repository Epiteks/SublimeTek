import sublime
import re

if not int(sublime.version()) >= 3000:
	import Parse
else:
	from . import Parse

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
			header.errors.append(Parse.Error("BADHEAD", "", "HEAD"))

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
