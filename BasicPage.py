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

def download(mode: str, input2: str, currentdirectory: str, ext: str):
	print(f"Downloading '{input2}' to '{currentdirectory}'...")

	if len(mode) <= 0 or len(input2) <= 0 or len(currentdirectory) <= 0 or len(ext) <= 0: print("Invalid args"); return

	ytcomman = [
		"yt-dlp",
		"-f", f"b[ext={ext}]/b", # Download chosen format, but fallback to best format if not available
		"--recode", ext, # Re-encode if not available
		"-o", f"{currentdirectory}/%(title)s [%(id)s].%(ext)s",
	]

	if mode == "url":
		ytcomman.insert(len(ytcomman), input2)
	elif mode == "ytsearch":
		ytcomman.insert(len(ytcomman), f"ytsearch:{input2}")
	else:
		print("Invalid mode"); return

	ytcomman.insert(len(ytcomman), "--max-downloads")
	ytcomman.insert(len(ytcomman), "1")

	c = subprocess.run(ytcomman)
	print(c.returncode)

def createFrame(window):
	global frame
	frame = tk.Frame(window, width=600, height=380)
	frame.columnconfigure(2, weight=1)

	global showPage, hidePage
	def hidePage():
		frame.place_forget()
	def showPage():
		frame.place(y=34, h=-34, relwidth=1.0, relheight=1.0)


	# URL box
	urlLabel = tk.Label(frame, text="URL: ")
	urlLabel.grid(row=2, column=1, sticky="E")

	urlInputBox = tk.Entry(frame)
	urlInputBox.grid(row=2, column=2, columnspan=2, sticky="WE")

	# File format
	tk.Label(frame, text="Format: ").grid(row=5, column=1, sticky="E")

	fileformats = [
		"m4a",
		"mp4",
		"mp3",
		"webm"
	]

	fileformat = tk.StringVar()

	fileformatDropdown = tk.OptionMenu(frame, fileformat, *fileformats)
	fileformatDropdown.grid(row=5, column=2, columnspan=2, sticky="W")

	# Destination Directory
	tk.Label(frame, text="Destination directory: ").grid(row=19, column=1, sticky="E")

	dirSV = tk.StringVar()
	dirSV.set(getUserDownloadDir())

	dirInputBox = tk.Entry(frame, textvariable=dirSV)
	dirInputBox.grid(row=19, column=2, sticky="WE")

	def seldir():
		global currentdirectory
		global windowp
		windowp = tk.Toplevel(window)
		windowp.withdraw()
		picked_dir = filedialog.askdirectory()
		if isinstance(picked_dir, str) and len(picked_dir) > 0:
			dirSV.set(picked_dir)

	selectDirButton = tk.Button(frame, text="Pick...", command=seldir)
	selectDirButton.grid(row=19, column=3)

	global modenum
	modenum = 0
	def downloadf():
		input2 = urlInputBox.get().strip()
		if modenum == 0:
			download("url", input2, dirSV.get(), fileformat.get())
		elif modenum == 1:
			download("ytsearch", input2, dirSV.get(), fileformat.get())

	downloadButton = tk.Button(frame, text="Download", bg="yellow", command=downloadf)
	downloadButton.grid(row=20, column=1, columnspan=3, sticky="E")


	# Mode
	modeLabel = tk.Label(frame, text="Mode: ")
	modeLabel.grid(row=1,column=1,sticky="E")

	modes = [
		"Download from URL",
		"Search & Download from YouTube",
	]

	mode = tk.StringVar(value=modes[0])

	urlLabel
	def selection():
		global modenum
		modenum = modes.index(mode.get())
		if modenum == 0:
			urlLabel.config(text="URL: ")
		elif modenum == 1:
			urlLabel.config(text="Search term: ")
	selection()

	modeDropdown = tk.OptionMenu(frame, mode, *modes, command=lambda _: selection())
	modeDropdown.grid(row=1, column=2, columnspan=2, sticky="W")

