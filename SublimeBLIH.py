import sublime
import sublime_plugin
import re
import json
import os

if not int(sublime.version()) >= 3000:
	import BLIH
else:
	from . import BLIH

def	git_clone_repo(server, login, name, folder):
	route = str(login) + "@" + str(server) + ":/" + str(login) + "/" + str(name)
	print(route)

def	blih_get_projects(blih):
	result = blih.execute("repository", "list")
	repos = []
	if result and result["code"] == 200:
		for repo in result["data"]["repositories"]:
			repos.append(repo)
	repos.sort()
	return repos

def	output_display(window, data):
	output = window.create_output_panel("SublimeTek")
	window.run_command("show_panel", {"panel": "output.SublimeTek"})
	code = data["code"]
	message = ""
	for item in data["data"]:
		message += str(data["data"][item]) + "\n"
	result = {"code": code, "message": message}
	output.run_command("sublime_tek_blih_output", result)

class	SublimeTekBlihOutput(sublime_plugin.TextCommand):

	def	run(self, edit, **args):
		self.code = str(args["code"])
		self.message = str(args["message"])
		text = "Code " + self.code + "\n" + self.message
		self.view.insert(edit, 0, text)

class	SublimeTekBlihCreateRepoCommand(sublime_plugin.WindowCommand):

	def	run(self):
		settings = sublime.load_settings('SublimeTek.sublime-settings')
		self.login = settings.get("login")
		self.password = settings.get("unix_password")
		blih_settings = settings.get("BLIH")
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
				self.window.show_input_panel("Type folder location for this project", self.base_location, self.set_folder, None, None)
			else:
				self.set_folder(self.default_folder)
		else:
			output_display(self.window, self.result)

	def	set_folder(self, folder):
		#Add result for clone
		git_clone_repo(self.server, self.login, self.name, folder)
		output_display(self.window, self.result)

class	SublimeTekBlihDeleteRepoCommand(sublime_plugin.WindowCommand):

	def	remove_project(self, name):
		if name == self.name:
			result = self.blih.execute("repository", "delete", route=[name])
		else:
			result = {"code": 401, "data": {"message": "Wrong name for confirmation"}}
		output_display(self.window, result)

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
		git_clone_repo(self.server, self.login, self.name, folder)
		#Add result for clone
		# output_display(self.window, {"code": 400, "data": {"message": "Repository cloned"}})

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
		output_display(self.window, result)

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
