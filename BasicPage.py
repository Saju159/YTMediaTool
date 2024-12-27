import tkinter as tk
from tkinter import filedialog
import subprocess
import os
from sys import platform

def getUserDownloadDir():
	if platform == "linux":
		c = subprocess.run(["which", "xdg-user-dir"])
		if c.returncode == 0:
			c = subprocess.run(["xdg-user-dir", "DOWNLOAD"])
			if c.returncode == 0 and c.stdout:
				return c.stdout

	# fallback to a 'Downloads' directory in the user's home
	return os.path.expanduser("~/Downloads")

currentdirectory = getUserDownloadDir()

def download(modenum, input2):
	print("Downloading...")

	print(input2)

	if modenum == 0:
		filename = subprocess.getoutput(f'yt-dlp {input2} --print filename {input2}')
		ytcomman = [
			"yt-dlp",
			"-f", "ba[ext=m4a]",
			"-o", f"{currentdirectory}/{filename}.m4a",
			input2,
			"--max-downloads", "1"
		]
	elif modenum == 1:
		filename = subprocess.getoutput(f'yt-dlp "ytsearch:{input2}", --print filename {input2}')
		ytcomman = [
			"yt-dlp",
			"-f", "ba[ext=m4a]",
			"-o", f"{currentdirectory}/{filename}.m4a",
			f"ytsearch:{input2}",
			"--max-downloads", "1"
		]

	if ytcomman:
		c = subprocess.run(ytcomman)
		print(c.returncode)
	else:
		print("No command")

def createFrame(window):
	global frame
	frame = tk.Frame(window, width=600, height=380)

	global showPage, hidePage
	def hidePage():
		frame.place_forget()
	def showPage():
		frame.place(y=34)

	lm = tk.Label(frame, text = "Toimintatila:")
	lm.config(font =("Courier", 14))
	lm.place(x=5, y=5)

	def seldir():
		global currentdirectory
		global windowp
		windowp = tk.Toplevel(window)
		windowp.withdraw()
		picked_dir = filedialog.askdirectory()
		if isinstance(picked_dir, str):
			currentdirectory = picked_dir

		lm = tk.Label(frame, text = "Nykyinen kohdekansio: " + currentdirectory)
		lm.config(font =("Courier", 14))
		lm.place(x=5, y=130)

	global l1, l2, seldirb, input1
	l1, l2, seldirb, input1 = None, None, None, None

	input1 = tk.Text(frame, height = 1, width = 50)
	input1.place(x=110, y=  60)

	def downloadf():
		input2 = input1.get("1.0", "end").strip()
		download(modenum, input2)

	downloadb=tk.Button(frame, text="Lataa",bg="yellow", command=downloadf)
	downloadb.place(x=5, y= 90)

	seldirb=tk.Button(frame, text="Valitse kohdekansio",bg="yellow", command=seldir)
	seldirb.place(x=80, y= 90)

	def show():
		tk.Label.config( text = mode.get() )

	modes = [
		"URL lataus",
		"Lataus Hakusanalla",
	]

	mode = tk.StringVar(value=modes[0])

	def selection():
		global modenum
		modenum = modes.index(mode.get())
		global l1, l2, download, seldirb, input1

		if l1: l1.destroy()
		if l2: l2.destroy()

		if modenum == 0:
			l1 = tk.Label(frame, text = "URL:")
			l1.config(font =("Courier", 14))
			l1.place(x=5, y=60)

			#l2.destroy()

		if modenum == 1:
			l2 = tk.Label(frame, text = "Hakusana:")
			l2.config(font =("Courier", 14))
			l2.place(x=5, y=60)

			#l1.destroy()

	selection()

	drop = tk.OptionMenu( frame , mode , *modes, command=lambda _: selection())
	drop.place(x=155, y=0 )

