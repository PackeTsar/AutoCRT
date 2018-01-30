#!/usr/bin/python

import os
import sys


class auto_engine:
	def __init__(self, options, args):
		global threading
		global ConnectHandler
		import threading
		from netmiko import ConnectHandler
		self.options = options
		self.args = args
		#self.optiondict = vars(options)
		self._set_opts()
		self.master = {}
		self.run()
		#self.thread = threading.Thread(target=self.run)
		#self.thread.daemon = True
		#self.thread.start()
	def _get_template(self):
		f = open(self.options["template"], "r")
		self.options["templatedata"] = f.readlines()
		f.close()
	def _check_inputs(self, arglist, data):
		for arg in arglist:
			if type(arg) == type(()):
				if not data[arg[0]] and not data[arg[1]]:
					return False
			elif not data[arg]:
				return False
		return True
	def _fix_dir(self, cwd):
		# Add a slash at end of directory path if one not there
		if "\\" in cwd:  # If a Windows path
			if cwd[len(cwd)-1] != "\\":
				cwd += "\\"
		elif "/" in cwd:  # If a Linux path
			if cwd[len(cwd)-1] != "/":
				cwd += "/"
		else:
			if "\\" in os.getcwd():
				cwd += "\\"
			elif "/" in os.getcwd():  # If a Linux path
				cwd += "/"
		return cwd
	def _ip_range(self, iprange):
		import netaddr
		global glob_error
		ipsplit = iprange.split("-")
		try:
			iprange = netaddr.iter_iprange(ipsplit[0], ipsplit[1])
		except:
			glob_error = "Bad IP Range. Example: 192.168.1.1-192.168.1.100"
			return []
		result = list(iprange)
		if result == []:
			glob_error = "Bad IP Range. Example: 192.168.1.1-192.168.1.100"
			return []
		return result
	def _set_opts(self):
		if self.options["output_folder"] == None:
			self.options["output_folder"] = self._fix_dir(os.getcwd())
		else:
			self.options["output_folder"] = self._fix_dir(self.options["output_folder"])
		if self.options["device_type"] == None:
			self.options["device_type"] = "cisco_ios"
	def run(self):
		global glob_error
		reqopts = [("hostname", "range"), "template", "user", "password"]
		if not self._check_inputs(reqopts, self.options):
			glob_error = "Missing inputs!. Must provide: (hostname or range), template, user, and password"
		elif self.options["range"]:
			self._get_template()
			for ipobj in self._ip_range(self.options["range"]):
				localopts = self.options
				localopts.update({"hostname": str(ipobj)})
				self.master.update({self.options["hostname"]: auto_make(localopts)})
		elif self.options["hostname"]:
			self._get_template()
			self.master.update({self.options["hostname"]: auto_make(self.options)})


class auto_make:
	def __init__(self, options):
		self.hostname = options["hostname"]
		self.user = options["user"]
		self.password = options["password"]
		self.templatedata = options["templatedata"]
		self.output_folder = options["output_folder"]
		self.device_type = options["device_type"]
		self.ui_type = options["ui_type"]
		self.status = auto_status(self.hostname, self.ui_type)
		#self.run()
		self.thread = threading.Thread(target=self.run)
		self.thread.daemon = True
		self.thread.start()
	def run(self):
		self._check_dir()
		name = self._get_name()
		if not self.status()["error"]:
			#print(name)
			self._make_ini(name)
	def _check_dir(self):
		self.status.update("status", "Checking for folder")
		if os.path.isdir(self.output_folder):
			self.status.update("status", "Folder Exists")
			self.status.update("folder_created", True)
		else:
			self.status.update("status", "Folder does not exist, creating...")
			self.status.update("folder_created", False)
			os.makedirs(self.output_folder)
			self.status.update("status", "Folder created")
			self.status.update("folder_created", True)
	def _get_name(self):
		self.status.update("status", "Trying to connect")
		try:
			device = ConnectHandler(**{
				'device_type': self.device_type,
				'ip': self.hostname,
				'username': self.user,
				'password': self.password,
				})
			self.status.update("status", "Logged in successfully")
			self.status.update("connected", True)
			name = device.find_prompt()
			name = name.replace("#", "")
			self.status.update("device_name", name)
			device.disconnect()
			self.status.update("connected", False)
			return name
		except Exception as e:
			self.status.update("status", e)
			self.status.update("status", "Failed")
			self.status.update("error", e)
			self.status.update("alive", False)
	def _make_ini(self, name):
		newdata = ""
		for line in self.templatedata:
			if 'S:"Hostname"=' in line:
				newdata += 'S:"Hostname"=%s\n' % self.hostname
			else:
				newdata += line
		filename = name + ".ini"
		self.status.update("status", "Creating "+filename)
		f = open(self.output_folder+filename, "w")
		f.write(newdata)
		f.close()
		self.status.update("status", "Sucessful")
		self.status.update("ini_created", True)
		self.status.update("alive", False)


class auto_status:
	def __init__(self, name, ui_type):
		self.name = name
		self.log = []
		if ui_type == "cli":
			self._mode_cli()
		else:
			self._mode_gui()
	def _mode_cli(self):
		self.status = None
		self.error = None
		self.connected = False
		self.device_name = "Unknown"
		self.folder_created = None
		self.ini_created = False
		self.alive = True
		self._attribs = {
			"name": self.name,
			"status": self.status,
			"error": self.error,
			"connected": self.connected,
			"device_name": self.device_name,
			"folder_created": self.folder_created,
			"ini_created": self.ini_created,
			"alive": self.alive
			}
		self.__call__ = self._cli_get
	def _mode_gui(self):
		self.connected = False
		self.device_name = "Unknown"
		self.folder_created = False
		self.ini_created = False
		self.__call__ = self._gui_get
	def update(self, attrib, value):
		#print(attrib, value)
		self._attribs[attrib] = value
		if attrib == "status":
			self.log.append(value)
	def _cli_get(self):
		return self._attribs
	def _gui_get(self):
		return "GUI OBJECZTS"


class ui_cli:
	def __init__(self, options, args):
		global re
		global glob_error
		import re
		glob_error = None
		self.options = options
		self.args = args
		self.options.update({"ui_type": "cli"})
		self.engine = auto_engine(self.options, args)
		if self.options["range"]:
			self.show_progress()
		else:
			self.show_single()
	class screen:
		def __init__(self):
			global curses
			import curses
			self.win = curses.initscr()
			self.onscreen = None
			curses.noecho()
			curses.cbreak()
		def write(self, data):
			if data != self.onscreen:
				linelist = data.split("\n")
				index = 0
				self.win.clear()
				for line in linelist:
					self.win.addstr(index, 0, line)
					index += 1
				self.win.refresh()
				self.onscreen = data
	def _gen_animation(self):
		l = ["\\", "|", "/", "-"]
		index = 0
		while True:
			if index == 3:
				yield l[index]
				index = 0
			else:
				yield l[index]
				index += 1
	def show_progress(self):
		scr = self.screen()
		ani = self._gen_animation()
		try:
			while not glob_error:
				data = []
				parse = self.engine.master
				for each in parse:
					data.append(self.engine.master[each].status())
				order = ["name", "folder_created", "connected", "device_name", "ini_created", "error", "status"]
				scr.write(self.make_table(order, data))
			curses.echo()
			curses.nocbreak()
			curses.endwin()
			print(glob_error)
			sys.exit()
		except:
			curses.echo()
			curses.nocbreak()
			curses.endwin()
			sys.exit()
	def show_single(self):
		current = None
		loop = True
		index = 0
		while loop:
			try:
				log = self.engine.master[self.options["hostname"]].status.log
				alive = self.engine.master[self.options["hostname"]].status()["alive"]
				while log[len(log)-1] != current:
					current = log[index]
					print(current)
					index += 1
				if not alive:
					loop = False
			except KeyError:
				pass
	def make_table(self, columnorder, tabledata):
		##### Check and fix input type #####
		if type(tabledata) != type([]): # If tabledata is not a list
			tabledata = [tabledata] # Nest it in a list
		##### Set seperators and spacers #####
		tablewrap = "#" # The character used to wrap the table
		headsep = "=" # The character used to seperate the headers from the table values
		columnsep = "|" # The character used to seperate each value in the table
		columnspace = "  " # The amount of space between the largest value and its column seperator
		##### Generate a dictionary which contains the length of the longest value or head in each column #####
		datalengthdict = {} # Create the dictionary for storing the longest values
		for columnhead in columnorder: # For each column in the columnorder input
			datalengthdict.update({columnhead: len(columnhead)}) # Create a key in the length dict with a value which is the length of the header
		for row in tabledata: # For each row entry in the tabledata list of dicts
			for item in columnorder: # For column entry in that row
				if len(re.sub(r'\x1b[^m]*m', "",  str(row[item]))) > datalengthdict[item]: # If the length of this column entry is longer than the current longest entry
					datalengthdict[item] = len(str(row[item])) # Then change the value of entry
		##### Calculate total table width #####
		totalwidth = 0 # Initialize at 0
		for columnwidth in datalengthdict: # For each of the longest column values
			totalwidth += datalengthdict[columnwidth] # Add them all up into the totalwidth variable
		totalwidth += len(columnorder) * len(columnspace) * 2 # Account for double spaces on each side of each column value
		totalwidth += len(columnorder) - 1 # Account for seperators for each row entry minus 1
		totalwidth += 2 # Account for start and end characters for each row
		##### Build Header #####
		result = tablewrap * totalwidth + "\n" + tablewrap # Initialize the result with the top header, line break, and beginning of header line
		columnqty = len(columnorder) # Count number of columns
		for columnhead in columnorder: # For each column header value
			spacing = {"before": 0, "after": 0} # Initialize the before and after spacing for that header value before the columnsep
			spacing["before"] = int((datalengthdict[columnhead] - len(columnhead)) / 2) # Calculate the before spacing
			spacing["after"] = int((datalengthdict[columnhead] - len(columnhead)) - spacing["before"]) # Calculate the after spacing
			result += columnspace + spacing["before"] * " " + columnhead + spacing["after"] * " " + columnspace # Add the header entry with spacing
			if columnqty > 1: # If this is not the last entry
				result += columnsep # Append a column seperator
			del spacing # Remove the spacing variable so it can be used again
			columnqty -= 1 # Remove 1 from the counter to keep track of when we hit the last column
		del columnqty # Remove the column spacing variable so it can be used again
		result += tablewrap + "\n" + tablewrap + headsep * (totalwidth - 2) + tablewrap + "\n" # Add bottom wrapper to header
		##### Build table contents #####
		result += tablewrap # Add the first wrapper of the value table
		for row in tabledata: # For each row (dict) in the tabledata input
			columnqty = len(columnorder) # Set a column counter so we can detect the last entry in this row
			for column in columnorder: # For each value in this row, but using the correct order from column order
				spacing = {"before": 0, "after": 0} # Initialize the before and after spacing for that header value before the columnsep
				spacing["before"] = int((datalengthdict[column] - len(re.sub(r'\x1b[^m]*m', "",  str(row[column])))) / 2) # Calculate the before spacing
				spacing["after"] = int((datalengthdict[column] - len(re.sub(r'\x1b[^m]*m', "",  str(row[column])))) - spacing["before"]) # Calculate the after spacing
				result += columnspace + spacing["before"] * " " + str(row[column]) + spacing["after"] * " " + columnspace # Add the entry to the row with spacing
				if columnqty == 1: # If this is the last entry in this row
					result += tablewrap + "\n" + tablewrap # Add the wrapper, a line break, and start the next row
				else: # If this is not the last entry in the row
					result += columnsep # Add a column seperator
				del spacing # Remove the spacing settings for this entry 
				columnqty -= 1 # Keep count of how many row values are left so we know when we hit the last one
		result += tablewrap * (totalwidth - 1) # When all rows are complete, wrap the table with a trailer
		return result


class ui_gui:
	def __init__(self, options, args):
		print("No GUI for you yet!")
		print("Run with '-h' switch for help")
		#self.args = args
		#print("GUI")
		#print(options)
		#print(args)
		#self.root = tk.Tk()
		##self.gui = gui(self.root)
		#self.root.title("AutoCRT")
		#self.root.geometry('1080x700')
		##self.root.attributes('-alpha', .80) # Transparency
		#self.root.grid_columnconfigure(0, weight=1)
		#self.root.grid_rowconfigure(1, weight=1)
		##logo = tk.PhotoImage(data=logoimagedata)
		##self.root.tk.call('wm','iconphoto',self.root._w,logo)
		######################
		#checkbuttonframe = tk.Frame(self.root)
		#checkbuttonframe.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
		#checkbuttonframe.grid_columnconfigure(1, weight=1)
		##self.newcheckbuttonimage = tk.PhotoImage(data=newcheckimagedata)
		##newcheckbutton = tk.Button(checkbuttonframe, image=self.newcheckbuttonimage, text='+', command=self.create_check)
		##newcheckbutton.grid(row=0, column=0, sticky="nw")
		#checkallframe = tk.Frame(checkbuttonframe)
		#checkallframe.grid(row=0, column=1, padx=87, sticky="nw")
		##self.runallbuttonimage = tk.PhotoImage(data=runallimagedata)
		##checkallbutton = tk.Button(checkallframe, image=self.runallbuttonimage, command= lambda: core.run_all())
		##checkallbutton.grid(row=0, column=0)
		##self.configentry = ttk.Combobox(checkbuttonframe, width=25, justify=tk.CENTER)
		##self.configentry.grid(row=0, column=2, sticky="e")
		##self.configentry.bind("<<ComboboxSelected>>", lambda evente:self._config_file_populate(self.configentry))
		##self.savebuttonimage = tk.PhotoImage(data=saveimagedata)
		##savebutton = tk.Button(checkbuttonframe, image=self.savebuttonimage, command= lambda: core.save_config())
		##savebutton.grid(row=0, column=3, sticky="e")
		#self.root.mainloop()


if __name__ == "__main__":
	def _opts_exist(options):
		options = vars(options)
		for option in options:
			if options[option] != None:
				return True
		return False
	def _py3_gui():
		try:
			global tk
			import tkinter as tk
			return True
		except ImportError:
			return False
	def _py2_gui():
		try:
			global tk
			import Tkinter as tk
			return True
		except ImportError:
			return False
	from optparse import OptionParser
	parser = OptionParser()
	parser.add_option("-t", "--template", dest="template",
		help=".INI file to use for template", metavar="TEMPLATE")
	parser.add_option("-l", "--user", dest="user",
		help="SSH login name to use", metavar="USER")
	parser.add_option("-w", "--password", dest="password",
		help="SSH password to use", metavar="PASSWORD")
	parser.add_option("-o", "--output_folder", dest="output_folder",
		help="Folder where .INI file is created", metavar="OUTPUT_FOLDER")
	parser.add_option("-i", "--hostname", dest="hostname",
		help="IP address or hostname of remote device", metavar="HOSTNAME")
	parser.add_option("-r", "--range", dest="range",
		help="IP address range of hosts to find", metavar="RANGE")
	parser.add_option("-d", "--device_type", dest="device_type",
		help="Device Type", metavar="DEVICE_TYPE")
	(options, args) = parser.parse_args()
	if _opts_exist(options):
		ui_cli(vars(options), args)
	elif _py3_gui() or _py2_gui():
		ui_gui(options, args)
	else:
		ui_cli(vars(options), args)