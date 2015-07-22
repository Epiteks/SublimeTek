import json
import hmac
import hashlib
import urllib.request
import urllib.parse

class	Request():

	def	__init__(self, url, method, data):
		self.done = False
		self.url = url
		self.method = method
		self.data = bytes(json.dumps(data), "utf8")
		self.error = None
		self.make()

	def	make(self):
		self.request = urllib.request.Request(url=self.url, method=self.method)
		self.request.add_data(self.data)
		self.request.add_header("Content-Type", "application/json")

	def	execute(self):
		self.done = True
		try:
			self.result = urllib.request.urlopen(self.request)
		except urllib.error.HTTPError as e:
			data = json.loads(e.read().decode("utf8"))
			self.error = {"code": e.code, "data": data}
			return False
		return True

	def	parse(self):
		if self.done and not self.error and self.result.status == 200:
			try:
				raw_data = json.loads(self.result.read().decode("utf8"))
				data = {"code": self.result.status, "data": raw_data}
			except:
				return None
			return data
		return None

class	BLIH():

	def	__init__(self, login, token):
		self.base = "https://blih.epitech.eu/"
		self.login = login
		self.token = bytes(token, "utf8")
		with open("./BLIHAPI.json") as data:
			self.actions = json.load(data)

	def	make_body(self, data):
		hash_signature = hmac.new(self.token, msg=bytes(self.login, 'utf-8'), digestmod=hashlib.sha512)
		if data:
			hash_signature.update(bytes(json.dumps(data, sort_keys=True, indent=4, separators=(',', ': ')), 'utf8'))
		signature = hash_signature.hexdigest()
		result = {"user": self.login, "signature": signature}
		if data:
			result["data"] = data
		return result

	def	get_action(self, user_mode, user_action):
		if user_mode in self.actions:
			for action in self.actions[user_mode]:
				if action["action"] == user_action:
					return action
		return None

	def	get_route(self, action, args):
		find = action["route"].find("$")
		index = 0
		while find != -1:
			action["route"] = action["route"].replace("$", args[index], 1)
			index += 1
			find = action["route"].find("$")
		return action["route"]

	def	get_data(self, action, args):
		index = 0
		data = {}
		if action["data"]:
			for arg in action["data"]:
				if len(args) > index:
					data[arg["name"]] = args[index]
				elif not arg["optional"] and arg["default"]:
					data[arg["name"]] = arg["default"]
				index += 1
		if data == {}:
			return None
		return data

	def	check_args(self, action, route, body):
		if action["arguments"]:
			route_args = len(action["arguments"])
		else:
			route_args = 0
		data_args = 0
		if action["data"]:
			for arg in action["data"]:
				if not arg["optional"] and not arg["default"]:
					data_args += 1
		if len(route) < route_args or (action["data"] and (len(body) > len(action["data"]) or len(body) < data_args)):
			return None
		return action

	def	make_args(self, action, route=[], body=[]):
		result = self.check_args(action, route, body)
		if not result:
			return None
		final_route = self.base + self.get_route(action, route)
		data = self.get_data(action, body)
		final_body = self.make_body(data)
		request = Request(final_route, action["method"], final_body)
		return request

	def	execute(self, user_mode, user_action, route=[], body=[]):
		action = self.get_action(user_mode, user_action)
		if action:
			request = self.make_args(action, route, body)
			if not request:
				return
			status = request.execute()
			if status:
				result = request.parse()
			else:
				result = request.error
			return result
