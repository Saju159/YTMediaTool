import os
import tkinter as tk
import tkinter.ttk as ttk
from Common import openFilePicker, getBaseConfigDir
from webbrowser import open_new_tab as openInBrowser
from sys import platform

import Settings

def createFrame(window):
	global frame
	frame = tk.Frame(window, width=600, height=380)
	frame.rowconfigure(1, weight=1)
	frame.columnconfigure(1, weight=1)

	scrollbar = ttk.Scrollbar(frame, orient="vertical")
	scrollbar.grid(row=1, column=2, sticky="NS")
	canvas = tk.Canvas(frame, yscrollcommand=scrollbar.set, highlightthickness=0)
	canvas.grid(row=1, column=1, sticky="NSWE")
	frame2 = tk.Frame(canvas, padx=4, pady=4)
	frame2_win = canvas.create_window(0, 0, window=frame2, anchor="nw")
	frame2.columnconfigure(1, weight=1)
	scrollbar.config(command=canvas.yview)

	canvas.xview_moveto(0)
	canvas.yview_moveto(0)

	nextRow = 1
	scrollable = False
	labels = []
	tkVars = {}

	def _frame2_reconf(event):
		canvas.config(scrollregion=f"0 0 {event.width} {event.height}")
		canvas.config(width=event.width)

		nonlocal labels
		width = event.width - 20
		for label in labels:
			label.config(wraplength=width)

	def _canvas_reconf(event):
		nonlocal scrollable
		scrollable = event.height <= frame2.winfo_height()
		canvas.itemconfigure(frame2_win, width=event.width)

	frame2.bind("<Configure>", _frame2_reconf)
	canvas.bind("<Configure>", _canvas_reconf)

	def _scroll(delta):
		if scrollable:
			canvas.yview_scroll(int(-1*delta), "units")

	applyBtn, undoBtn = None, None

	def loadSettings():
		for key in tkVars:
			if key in Settings.Settings:
				tkVars[key].set(Settings.Settings[key])
		applyBtn.configure(state="disabled")
		undoBtn.configure(state="disabled")

	def applySettings():
		for key in tkVars:
			if key in Settings.Settings:
				Settings.Settings[key] = tkVars[key].get()
		Settings.saveSettingsToFile()
		applyBtn.configure(state="disabled")
		undoBtn.configure(state="disabled")

	def showButtonsFrame():
		applyBtn.configure(state="normal")
		undoBtn.configure(state="normal")

	global showPage, hidePage
	def hidePage():
		frame.place_forget()
		frame.unbind_all("<MouseWheel>")
		frame.unbind_all("<Button-4>")
		frame.unbind_all("<Button-5>")
	def showPage():
		frame.place(y=34, h=-34, relwidth=1.0, relheight=1.0)
		window.after(1, lambda: window.config(height=480))
		# <MouseWheel> for windows and <Button-4/5> for linux/x11
		frame.bind_all("<MouseWheel>", lambda event: _scroll(event.delta/120))
		frame.bind_all("<Button-4>", lambda _: _scroll(3))
		frame.bind_all("<Button-5>", lambda _: _scroll(-3))
		loadSettings()

	def baseOptFrame():
		nonlocal nextRow
		optFrame = tk.Frame(frame2)
		optFrame.grid(row=nextRow, column=1, sticky="WE")
		nextRow += 1
		return optFrame

	def baseHelpBtn(text: str, optFrame: tk.Frame, column: int):
		btn = ttk.Button(optFrame, text="?", width=2, padding=0, command=lambda: tk.messagebox.showinfo("Help", text))
		btn.grid(row=1, column=column+1, sticky="W")
		optFrame.columnconfigure(column, minsize=4)

	def addLabel(text: str):
		nonlocal nextRow, labels
		label = ttk.Label(frame2, text=text, justify="left")
		label.grid(row=nextRow, column=1, sticky="W")
		labels.append(label)
		nextRow += 1

	def addButton(text: str, func: callable):
		nonlocal nextRow
		button = ttk.Button(frame2, text=text, command=lambda: func())
		button.grid(row=nextRow, column=1, sticky="W")
		nextRow += 1

	def addFilePathOption(optId: str, text: str, helptext: None=str|None):
		optFrame = baseOptFrame()
		optFrame.columnconfigure(2, weight=1)
		ttk.Label(optFrame, text=f"{text}: ").grid(row=1, column=1, sticky="E")

		pathSV = tk.StringVar()
		tkVars[optId] = pathSV

		pathInputBox = ttk.Entry(optFrame, textvariable=pathSV)

		def checkDiff():
			if pathSV.get() != Settings.Settings[optId]:
				showButtonsFrame()

		pathInputBox.bind("<Control-KeyRelease-a>", lambda _: pathInputBox.select_range(0, tk.END), pathInputBox.icursor(tk.END))
		pathInputBox.bind("<Control-KeyRelease-A>", lambda _: pathInputBox.select_range(0, tk.END), pathInputBox.icursor(tk.END))
		pathInputBox.bind('<KeyRelease>', lambda _: checkDiff())
		pathInputBox.grid(row=1, column=2, sticky="WE")

		def seldir():
			picked_dir = openFilePicker(window, "openFile")
			if picked_dir:
				pathSV.set(picked_dir)
				showButtonsFrame()

		selectDirButton = ttk.Button(optFrame, text="Browse...", command=seldir)
		selectDirButton.grid(row=1, column=3)

		if type(helptext) == str:
			baseHelpBtn(helptext, optFrame, 4)

	def addBooleanOption(optId: str, text: str, helptext: None=str|None):
		optFrame = baseOptFrame()

		boolSV = tk.BooleanVar()
		tkVars[optId] = boolSV

		def checkDiff():
			if boolSV.get() != Settings.Settings[optId]:
				showButtonsFrame()

		pathCheckbox = ttk.Checkbutton(optFrame, text=text, variable=boolSV, onvalue=True, offvalue=False, command=lambda: checkDiff())
		pathCheckbox.grid(row=1, column=1, sticky="W")

		if type(helptext) == str:
			baseHelpBtn(helptext, optFrame, 2)

	def addDropdownOption(optId: str, text: str, choices: list, helptext: None=str|None):
		optFrame = baseOptFrame()
		ttk.Label(optFrame, text=f"{text}: ").grid(row=1, column=1, sticky="E")

		sv = tk.StringVar()
		tkVars[optId] = sv

		def checkDiff(_):
			if sv.get() != Settings.Settings[optId]:
				showButtonsFrame()

		vqDropdown = ttk.OptionMenu(optFrame, sv, choices[0], *choices, command=checkDiff)
		vqDropdown.grid(row=1, column=2, sticky="W")

		if type(helptext) == str:
			baseHelpBtn(helptext, optFrame, 3)

	def addSpacer():
		nonlocal nextRow
		tk.Label(frame2, text="\n ").grid(row=nextRow)
		nextRow += 1

	def addShortSpacer():
		nonlocal nextRow
		frame2.rowconfigure(nextRow, minsize=12)
		nextRow += 1

	addFilePathOption("FFmpeg_path", "Path to FFmpeg executable")
	addLabel("FFmpeg is required for merging the downloaded video + audio and for converting formats.")
	if platform == "win32":
		addButton("Download FFmpeg for Windows from github.com/BtbN/FFmpeg-Builds", lambda: openInBrowser("https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"))
	addButton("Get binaries from https://www.ffmpeg.org/download.html", lambda: openInBrowser("https://www.ffmpeg.org/download.html"))

	addSpacer()
	addLabel("Settings for 'Basic' tab:")
	addBooleanOption("YDL-EnablePlaylistDL", "Download playlist if URL leads to both a video and a playlist")
	addBooleanOption("YDL-SkipIfExists", "Skip download if already downloaded", "Will still show \"Download completed\" even if the file was already downloaded.")
	addBooleanOption("BasicPage-ShowDialogAfterDLSuccess", "Show dialog after successful download")
	addDropdownOption("BasicPage-ForceQuality", "When video quality is not available", ["Resize to selected quality", "Download closest to selected quality"], "If \"Resize to selected quality\" is selected:\nCalls FFmpeg to resize the video after download if resolution doesn't match. This can be quite slow depending on the video's length and quality selected.")
	addShortSpacer()
	addFilePathOption("YDL-CookiesFilePath", "Path to cookies.txt", "Path to a Netscape formatted cookies file.\nLeave blank to not use a cookie file.\n\nCookies should only be used if you keep getting blocked by YouTube or are downloading private videos.\n\nDisables \"Grab browser cookies\".")
	addBooleanOption("BasicPage-Cookies", "Grab browser cookies", "Allows yt-dlp to grab your browser's cookies for authentication.\n\nIgnored if path to cookies.txt is not blank.")
	addDropdownOption("BasicPage-browser", "Browser to grab cookies from", ["brave", "chrome", "chromium", "edge", "firefox", "opera", "safari", "vivaldi", "whale"], "This list is populated with browsers that yt-dlp supports grabbing cookies from.")

	addSpacer()
	addLabel("Settings for 'SMLD' tab:")
	addButton("Open SMLD logs", lambda: openInBrowser(os.path.join(getBaseConfigDir(),"SMLD","SMLDlog.txt")))
	addDropdownOption("SMLD-mutithreading", "Number of concurrent downloads WARNING! THIS IS AN EXPERIMENTAL FEATURE", [1,2,4,8,16])
	addDropdownOption("SMLD-source", "Select the media download source", ["YouTube Music", "YouTube"])

	buttonsFrame = tk.Frame(frame, padx=4, pady=4)
	buttonsFrame.columnconfigure(2, pad=4)
	buttonsFrame.grid(row=2, column=1, columnspan=2, sticky="E")
	applyBtn = ttk.Button(buttonsFrame, text="Apply & Save changes", command=lambda: applySettings())
	applyBtn.grid(row=1, column=1, sticky="E")
	undoBtn = ttk.Button(buttonsFrame, text="Undo", command=lambda: loadSettings())
	undoBtn.grid(row=1, column=2, sticky="E")
