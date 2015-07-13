import sublime
import sublime_plugin
import re

if not int(sublime.version()) >= 3000:
	import Parse
	import Norme
else:
	from . import Parse
	from . import Norme

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
				elif item.code == Parse.ErrorCode.value("NOHEAD") or item.code == Parse.ErrorCode.value("BADHEAD"):
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

	def	test(self, val):
		print (val)

	def	pop_errors(self, errors):
		return

	def	show_errors(self, file):
		errors = Parse.Highlight()
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
		Norme.Norme.header(file.header)
		Norme.Norme.includes(file.includes)
		if len(file.functions) > 5:
			file.errors.append(Parse.Error("NBFUNCS", "", "FILE"))
		for function in file.functions:
			Norme.Norme.function(function)
		self.show_errors(file)

	def	run(self, edit):
		syntax = self.get_syntax()
		if syntax != "C":
			return
		file = self.get_file()
		self.execute(edit, file)
