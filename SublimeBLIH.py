import sublime
import sublime_plugin
import re
import json
import os
import subprocess

if not int(sublime.version()) >= 3000:
	import BLIH
else:
	from . import BLIH

def	git_clone_repo(command):
	try:
		res = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
	except Exception as e:
		result = {"code": 400, "data": {"message": str(e)}}
		return result
	result = {"code": 200, "data": {"message": "Repository cloned"}}
	return result

def	blih_get_projects(blih):
	result = blih.execute("repository", "list")
	repos = []
	if result and result["code"] == 200:
		for repo in result["data"]["repositories"]:
			if repo != "":
				repos.append(repo)
	repos.sort()
	return repos

def	output_display(window, data):
	output = window.create_output_panel("SublimeTek")
	window.run_command("show_panel", {"panel": "output.SublimeTek"})
	text = ""
	for msg in data:
		code = msg["code"]
		message = ""
		for item in msg["data"]:
			message += str(msg["data"][item]) + "\n"
			if text != "":
				text += "\n"
			text += "Code " + str(code) + "\n" + str(message)
	result = {"text": text}
	output.run_command("sublime_tek_blih_output", result)

def	replacer(action, repo="", location="", route=""):
	print("B4:" + str(action))
	settings = sublime.load_settings("SublimeTek.sublime-settings")
	blih = settings.get("BLIH")
	action = action.replace("$login", settings.get("login")).replace("$server", blih.get("server"))
	action = action.replace("$route", route).replace("$repo", repo).replace("$location", location)
	print("AFTR:" + str(action))
	return action

class	SublimeTekBlihOutput(sublime_plugin.TextCommand):

	def	run(self, edit, **args):
		text = args["text"]
		self.view.insert(edit, 0, text)

class	SublimeTekBlihCreateRepoCommand(sublime_plugin.WindowCommand):

	def	run(self):
		self.settings = sublime.load_settings('SublimeTek.sublime-settings')
		self.login = self.settings.get("login")
		self.password = self.settings.get("unix_password")
		blih_settings = self.settings.get("BLIH")
		self.auto_clone = blih_settings.get("auto_clone")
		self.ask_folder_clone = blih_settings.get("ask_for_folder_at_clone")
		self.default_folder = blih_settings.get("rendu_folder")
		self.base_location = blih_settings.get("base_location")
		if not self.base_location:
			self.base_location = os.getenv("HOME")
		self.server = blih_settings.get("server")
		self.window.show_input_panel("Type project name", "", self.create_project, None, None)

	def	create_project(self, name):
		self.name = name
		self.blih = BLIH.BLIH(self.login, self.password)
		self.result = self.blih.execute("repository", "create", body=[self.name])
		if self.result["code"] == 200 and self.auto_clone:
			if self.ask_folder_clone:
				self.window.show_input_panel("Type folder location for this project", str(self.base_location) + str(name), self.set_folder, None, None)
			else:
				self.set_folder(self.default_folder)
		else:
			output_display(self.window, [self.result])

	def	set_folder(self, folder):
		route = replacer(self.settings.get("BLIH").get("route"), repo=self.name)
		command = replacer(self.settings.get("BLIH").get("clone_command"), location=folder, route=route)
		result = git_clone_repo(command)
		output_display(self.window, [self.result, result])

class	SublimeTekBlihDeleteRepoCommand(sublime_plugin.WindowCommand):

	def	remove_project(self, name):
		if name == self.name:
			result = self.blih.execute("repository", "delete", route=[name])
		else:
			result = {"code": 401, "data": {"message": "Wrong name for confirmation"}}
		output_display(self.window, [result])

	def	confirm(self, index):
		if index != -1:
			self.name = self.repos[index]
			self.window.show_input_panel("Retype project name to confirm deletion (" + self.name + ")", "", self.remove_project, None, None)

	def	run(self):
		settings = sublime.load_settings('SublimeTek.sublime-settings')
		self.login = settings.get("login")
		self.password = settings.get("unix_password")
		self.blih = BLIH.BLIH(self.login, self.password)
		self.repos = blih_get_projects(self.blih)
		self.window.show_quick_panel(self.repos, self.confirm)

class	SublimeTekBlihCloneRepoCommand(sublime_plugin.WindowCommand):

	def	set_folder(self, folder):
		result = git_clone_repo(self.server, self.login, self.name, folder)
		output_display(self.window, [result])

	def	confirm(self, index):
		if index != -1:
			self.name = self.repos[index]
			if self.ask_folder_clone:
				self.window.show_input_panel("Type folder location for this project", self.base_location, self.set_folder, None, None)
			else:
				self.set_folder(self.default_folder)

	def	run(self):
		settings = sublime.load_settings('SublimeTek.sublime-settings')
		self.login = settings.get("login")
		self.password = settings.get("unix_password")
		self.blih = BLIH.BLIH(self.login, self.password)
		self.repos = blih_get_projects(self.blih)
		blih_settings = settings.get("BLIH")
		self.ask_folder_clone = blih_settings.get("ask_for_folder_at_clone")
		self.default_folder = settings.get("rendu_folder")
		self.base_location = blih_settings.get("base_location")
		if not self.base_location:
			self.base_location = os.getenv("HOME")
		self.server = blih_settings.get("server")
		self.window.show_quick_panel(self.repos, self.confirm)

class	SublimeTekBlihGetAclsRepoCommand(sublime_plugin.WindowCommand):

	def	get_acls(self):
		result = self.blih.execute("repository", "getacl", route=[self.name])
		data = result["data"]
		for item in data:
			right = data[item]
			self.acls.append([item, right])

	def	show_acls(self):
		self.window.show_quick_panel(self.acls, None)

	def	confirm(self, index):
		if index != -1:
			self.name = self.repos[index]
			self.get_acls()
			self.show_acls()

	def	run(self):
		settings = sublime.load_settings('SublimeTek.sublime-settings')
		self.login = settings.get("login")
		self.password = settings.get("unix_password")
		self.blih = BLIH.BLIH(self.login, self.password)
		self.repos = blih_get_projects(self.blih)
		self.acls = []
		self.window.show_quick_panel(self.repos, self.confirm)

class	SublimeTekBlihSetAclsRepoCommand(sublime_plugin.WindowCommand):

	def	set_acls(self, rights):
		result = self.blih.execute("repository", "setacl", route=[self.name], body=[self.user_set, rights])
		output_display(self.window, [result])

	def	ask_acls(self, name):
		self.user_set = name
		self.window.show_input_panel("Type rights for " + self.user_set + " (r/w/a/None to remove ACLs)", "", self.set_acls, None, None)

	def	confirm(self, index):
		if index != -1:
			self.name = self.repos[index]
			self.window.show_input_panel("Type user login", "", self.ask_acls, None, None)

	def	run(self):
		settings = sublime.load_settings('SublimeTek.sublime-settings')
		self.login = settings.get("login")
		self.password = settings.get("unix_password")
		self.blih = BLIH.BLIH(self.login, self.password)
		self.repos = blih_get_projects(self.blih)
		self.acls = []
		self.window.show_quick_panel(self.repos, self.confirm)
