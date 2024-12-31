import tkinter as tk
from tkinter import filedialog
import subprocess
import os
from sys import platform

def getUserDownloadDir():
	if platform == "linux":
		c = subprocess.run(["which", "xdg-user-dir"], stdout=subprocess.PIPE)
		if c.returncode == 0:
			c = subprocess.run(["xdg-user-dir", "DOWNLOAD"], capture_output=True)
			if c.returncode == 0:
				pathStr = str(c.stdout)
				pathStr = pathStr[:len(pathStr)-3][2:]
				return pathStr

	# fallback to a 'Downloads' directory in the user's home
	return os.path.expanduser("~/Downloads")

def openDirInFileBrowser(directory: str):
	if platform == "linux":
		c = subprocess.run(["which", "xdg-open"], stdout=subprocess.PIPE)
		if c.returncode == 0:
			subprocess.run(["xdg-open", directory], stdout=subprocess.PIPE)
		else:
			print("xdg-open not found! Can't open directory in system file browser!")
	elif platform == "win32":
		subprocess.run(["start", directory], stdout=subprocess.PIPE)

def openFilePicker(window: tk.Tk, dtype: str, **kwargs):
	window.update() # Prevent program from freezing if root window is killed while file picker is open
	title = "title" in kwargs and kwargs["title"] or None

	if platform == "linux":
		# Use kdialog if installed on linux for a better file picker.
		# Will check if kdialog is installed and if not, fallback to tkinter file picker for compatibility
		kdialog_installed = subprocess.run(["which", "kdialog"], stdout=subprocess.PIPE)
		if kdialog_installed.returncode == 0:
			pickerargs = ["kdialog"]
			if title:
				pickerargs.append("--title")
				pickerargs.append(title)

			if dtype == "openDir": pickerargs.append("--getexistingdirectory")
			elif dtype == "openFile": pickerargs.append("--getopenfilename")
			elif dtype == "saveFile": pickerargs.append("--getsavefilename")
			else: raise Exception("Invalid dtype! Must be 'openDir', 'openFile' or 'saveFile'")

			c = subprocess.run(pickerargs, stdout=subprocess.PIPE)
			if c.returncode == 0:
				pathStr = str(c.stdout)
				pathStr = pathStr[:len(pathStr)-3][2:]
				return pathStr
			else:
				return None

	# Fallback to tkinter picker (native on windows)
	picked = None
	if dtype == "openDir": picked = filedialog.askdirectory(parent=window, title=title, mustexist=True)
	elif dtype == "openFile": picked = filedialog.askopenfilename(parent=window, title=title)
	elif dtype == "saveFile": picked = filedialog.asksaveasfilename(parent=window, title=title)
	else: raise Exception("Invalid dtype! Must be 'openDir', 'openFile' or 'saveFile'")
	window.update()

	if picked and len(picked) > 0: return picked
	else: return None

