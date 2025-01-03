import tkinter as tk
from Common import openFilePicker
from webbrowser import open_new_tab as openInBrowser

import Settings

def createFrame(window):
	global frame
	frame = tk.Frame(window, width=600, height=380)
	frame.columnconfigure(2, weight=1)

	nextRow = 1
	labels = []
	tkVars = {}

	buttonsFrame = None

	def loadSettings():
		for key in tkVars:
			if key in Settings.Settings:
				tkVars[key].set(Settings.Settings[key])
		buttonsFrame.grid_forget()

	def applySettings():
		for key in tkVars:
			if key in Settings.Settings:
				Settings.Settings[key] = tkVars[key].get()
		Settings.saveSettingsToFile()
		buttonsFrame.grid_forget()

	def showButtonsFrame():
		buttonsFrame.grid(row=nextRow, column=1, columnspan=3, sticky="E")

	global showPage, hidePage
	def hidePage():
		frame.place_forget()
	def showPage():
		frame.place(y=34, h=-34, relwidth=1.0, relheight=1.0)
		loadSettings()

	def addLabel(text: str):
		nonlocal nextRow, labels
		label = tk.Label(frame, text=text, justify="left")
		label.grid(row=nextRow, column=1, columnspan=3, sticky="W", ipadx=10)
		labels.append(label)
		nextRow += 1
		return label

	def addButton(text: str, func: callable):
		nonlocal nextRow
		button = tk.Button(frame, text=text, command=lambda: func())
		button.grid(row=nextRow, column=1, columnspan=3, sticky="W")
		labels.append(button)
		nextRow += 1
		return button

	def addFilePathOption(optId: str, text: str):
		nonlocal nextRow
		tk.Label(frame, text=f"{text}: ").grid(row=nextRow, column=1, sticky="E")

		pathSV = tk.StringVar()
		tkVars[optId] = pathSV

		pathInputBox = tk.Entry(frame, textvariable=pathSV)

		def checkDiff():
			if pathSV.get() != Settings.Settings[optId]:
				showButtonsFrame()

		pathInputBox.bind('<KeyRelease>', lambda _: checkDiff())
		pathInputBox.grid(row=nextRow, column=2, sticky="WE")

		def seldir():
			picked_dir = openFilePicker(window, "openFile")
			if picked_dir:
				pathSV.set(picked_dir)
				showButtonsFrame()

		selectDirButton = tk.Button(frame, text="Browse...", command=seldir)
		selectDirButton.grid(row=nextRow, column=3)

		nextRow += 1

	def addBooleanOption(optId: str, text: str):
		nonlocal nextRow
		# tk.Label(frame, text=f"{text}: ").grid(row=nextRow, column=1, sticky="E")

		boolSV = tk.BooleanVar()
		tkVars[optId] = boolSV

		def checkDiff():
			if boolSV.get() != Settings.Settings[optId]:
				showButtonsFrame()

		pathCheckbox = tk.Checkbutton(frame, text=text, variable=boolSV, onvalue=True, offvalue=False, command=lambda: checkDiff())
		pathCheckbox.grid(row=nextRow, column=1, columnspan=3, sticky="W")

		nextRow += 1

	def addSpacer():
		nonlocal nextRow
		tk.Label(frame, text="\n ").grid(row=nextRow)
		nextRow += 1

	addFilePathOption("FFmpeg_path", "Path to FFmpeg executable")
	addLabel("FFmpeg is required for merging the downloaded video + audio and for converting formats.")
	addButton("Get binaries from https://www.ffmpeg.org/download.html", lambda: openInBrowser("https://www.ffmpeg.org/download.html"))

	addSpacer()
	addLabel("Settings for 'Basic' tab:")
	addBooleanOption("BasicPage-ShowDialogAfterDLSuccess", "Show dialog after successful download")

	buttonsFrame = tk.Frame(frame)
	tk.Button(buttonsFrame, text="Apply & Save Settings", bg="spring green", command=lambda: applySettings()).grid(row=1, column=1, sticky="E")
	tk.Button(buttonsFrame, text="Cancel", command=lambda: loadSettings()).grid(row=1, column=2, sticky="E")

	def onResize(event):
		nonlocal labels
		width = event.width - 20
		for label in labels:
			label.config(wraplength=width)

	frame.bind("<Configure>", onResize)
