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

def download(mode, input2, currentdirectory):
	print(f"Downloading '{input2}' to '{currentdirectory}'...")

	if mode == "url":
		ytcomman = [
			"yt-dlp",
			"-f", "ba[ext=m4a]",
			"-o", f"{currentdirectory}/%(title)s [%(id)s].%(ext)s",
			input2,
			"--max-downloads", "1"
		]
	elif mode == "ytsearch":
		ytcomman = [
			"yt-dlp",
			"-f", "ba[ext=m4a]",
			"-o", f"{currentdirectory}/%(title)s [%(id)s].%(ext)s",
			f"ytsearch:{input2}",
			"--max-downloads", "1"
		]
	else:
		print("Invalid mode")
		return

	if ytcomman:
		c = subprocess.run(ytcomman)
		print(c.returncode)
	else:
		print("No command")

def createFrame(window):
	global frame
	frame = tk.Frame(window, width=600, height=380)
	frame.columnconfigure(2, weight=1)

	global showPage, hidePage
	def hidePage():
		frame.place_forget()
	def showPage():
		frame.place(y=34, h=-34, relwidth=1.0, relheight=1.0)



	urlLabel = tk.Label(frame, text="URL: ")
	urlLabel.grid(row=2, column=1, sticky="E")

	urlInputBox = tk.Entry(frame)
	urlInputBox.grid(row=2, column=2, columnspan=2, sticky="WE")

	tk.Label(frame, text="Destination directory: ").grid(row=5, column=1, sticky="E")

	dirSV = tk.StringVar()
	dirSV.set(getUserDownloadDir())

	dirInputBox = tk.Entry(frame, textvariable=dirSV)
	dirInputBox.grid(row=5, column=2, sticky="WE")

	def seldir():
		global currentdirectory
		global windowp
		windowp = tk.Toplevel(window)
		windowp.withdraw()
		picked_dir = filedialog.askdirectory()
		if isinstance(picked_dir, str):
			dirSV.set(picked_dir)

	selectDirButton = tk.Button(frame, text="Pick...", command=seldir)
	selectDirButton.grid(row=5, column=3)

	global modenum
	modenum = 0
	def downloadf():
		input2 = urlInputBox.get().strip()
		if modenum == 0:
			download("url", input2, dirSV.get())
		elif modenum == 1:
			download("ytsearch", input2, dirSV.get())

	downloadButton = tk.Button(frame, text="Download", bg="yellow", command=downloadf)
	downloadButton.grid(row=20, column=1, columnspan=3, sticky="E")



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

