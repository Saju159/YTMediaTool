import os
import tkinter as tk
import tkinter.ttk as ttk
from Common import openFilePicker, getBaseConfigDir
from webbrowser import open_new_tab as openInBrowser
from sys import platform

import Settings

class Page(tk.Frame):
	def loadSettings(self):
		for key in self.tkVars:
			if key in Settings.Settings:
				self.tkVars[key].set(Settings.Settings[key])
		self.applyBtn.configure(state="disabled")
		self.undoBtn.configure(state="disabled")

	def _scroll(self, delta):
		if self.scrollable:
			self.canvas.yview_scroll(int(-1*delta), "units")

	def hidePage(self):
		self.Frame.place_forget()
		self.Frame.unbind_all("<MouseWheel>")
		self.Frame.unbind_all("<Button-4>")
		self.Frame.unbind_all("<Button-5>")

	def showPage(self):
		self.Frame.place(y=34, h=-34, relwidth=1.0, relheight=1.0)
		self.ParentWindow.after(1, lambda: self.ParentWindow.config(height=480))
		# <MouseWheel> for windows and <Button-4/5> for linux/x11
		self.Frame.bind_all("<MouseWheel>", lambda event: self._scroll(event.delta/120))
		self.Frame.bind_all("<Button-4>", lambda _: self._scroll(3))
		self.Frame.bind_all("<Button-5>", lambda _: self._scroll(-3))
		self.loadSettings()

	def __init__(self, window: tk.Tk):
		self.ParentWindow = window

		self.Frame = tk.Frame(window, width=600, height=380)
		self.Frame.rowconfigure(1, weight=1)
		self.Frame.columnconfigure(1, weight=1)

		scrollbar = ttk.Scrollbar(self.Frame, orient="vertical")
		scrollbar.grid(row=1, column=2, sticky="NS")
		self.canvas = tk.Canvas(self.Frame, yscrollcommand=scrollbar.set, highlightthickness=0)
		self.canvas.grid(row=1, column=1, sticky="NSWE")
		frame2 = tk.Frame(self.canvas, padx=4, pady=4)
		frame2_win = self.canvas.create_window(0, 0, window=frame2, anchor="nw")
		frame2.columnconfigure(1, weight=1)
		scrollbar.config(command=self.canvas.yview)

		self.canvas.xview_moveto(0)
		self.canvas.yview_moveto(0)

		nextRow = 1
		self.scrollable = False
		labels = []
		self.tkVars = {}

		def _frame2_reconf(event):
			self.canvas.config(scrollregion=f"0 0 {event.width} {event.height}")
			self.canvas.config(width=event.width)

			width = event.width - 20
			for label in labels:
				label.config(wraplength=width)

		def _canvas_reconf(event):
			self.scrollable = event.height <= frame2.winfo_height()
			self.canvas.itemconfigure(frame2_win, width=event.width)

		frame2.bind("<Configure>", _frame2_reconf)
		self.canvas.bind("<Configure>", _canvas_reconf)

		def applySettings():
			for key in self.tkVars:
				if key in Settings.Settings:
					Settings.Settings[key] = self.tkVars[key].get()
			Settings.saveSettingsToFile()
			self.applyBtn.configure(state="disabled")
			self.undoBtn.configure(state="disabled")

		def showButtonsFrame():
			self.applyBtn.configure(state="normal")
			self.undoBtn.configure(state="normal")

		def baseOptFrame():
			nonlocal nextRow
			optFrame = tk.Frame(frame2)
			optFrame.grid(row=nextRow, column=1, sticky="WE")
			nextRow += 1
			return optFrame

		def baseHelpBtn(text: str, optFrame: tk.Frame, column: int):
			def openHelpDialog():
				if text[:8] == "https://": # if helptext is just an url, open it in a browser since you can't copy from the tk dialog.
					openInBrowser(text)
				else:
					tk.messagebox.showinfo("Help", text)

			btn = ttk.Button(optFrame, text="?", width=2, padding=0, command=openHelpDialog)
			btn.grid(row=1, column=column+1, sticky="W")
			optFrame.columnconfigure(column, minsize=4)

		def addLabel(text: str):
			nonlocal nextRow
			label = ttk.Label(frame2, text=text, justify="left")
			label.grid(row=nextRow, column=1, sticky="W")
			labels.append(label)
			nextRow += 1

		def addButton(text: str, func: callable):
			nonlocal nextRow
			button = ttk.Button(frame2, text=text, command=lambda: func())
			button.grid(row=nextRow, column=1, sticky="W")
			nextRow += 1

		def addTextInputOption(optId: str, text: str, default: str|None, helptext: None=str|None):
			optFrame = baseOptFrame()
			optFrame.columnconfigure(2, weight=1)
			ttk.Label(optFrame, text=f"{text}: ").grid(row=1, column=1, sticky="E")

			pathSV = tk.StringVar()
			self.tkVars[optId] = pathSV

			inputBox = ttk.Entry(optFrame, textvariable=pathSV)

			def checkDiff():
				if pathSV.get() != Settings.Settings[optId]:
					showButtonsFrame()

			inputBox.bind("<Control-KeyRelease-a>", lambda _: inputBox.select_range(0, tk.END), inputBox.icursor(tk.END))
			inputBox.bind("<Control-KeyRelease-A>", lambda _: inputBox.select_range(0, tk.END), inputBox.icursor(tk.END))
			inputBox.bind('<KeyRelease>', lambda _: checkDiff())
			inputBox.grid(row=1, column=2, sticky="WE")

			if type(default) != None:
				defaultBtn = ttk.Button(optFrame, text="D", width=2, padding=0, command=lambda: pathSV.set(default))
				defaultBtn.grid(row=1, column=3, sticky="W")
				optFrame.columnconfigure(3, minsize=4)

			if type(helptext) == str:
				baseHelpBtn(helptext, optFrame, 4)

		def addFilePathOption(optId: str, text: str, helptext: None=str|None):
			optFrame = baseOptFrame()
			optFrame.columnconfigure(2, weight=1)
			ttk.Label(optFrame, text=f"{text}: ").grid(row=1, column=1, sticky="E")

			pathSV = tk.StringVar()
			self.tkVars[optId] = pathSV

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
			self.tkVars[optId] = boolSV

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
			self.tkVars[optId] = sv

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
		addTextInputOption("YDL-DLFilenameTemplate", "Filename Template", "%(title).165B.%(ext)s", "https://github.com/yt-dlp/yt-dlp?tab=readme-ov-file#output-template")
		addShortSpacer()
		addFilePathOption("YDL-CookiesFilePath", "Path to cookies.txt", "Path to a Netscape formatted cookies file.\nLeave blank to not use a cookie file.\n\nCookies should only be used if you keep getting blocked by YouTube or are downloading private videos.\n\nDisables \"Grab browser cookies\".")
		addBooleanOption("BasicPage-Cookies", "Grab browser cookies", "Allows yt-dlp to grab your browser's cookies for authentication.\n\nIgnored if path to cookies.txt is not blank.")
		addDropdownOption("BasicPage-browser", "Browser to grab cookies from", ["brave", "chrome", "chromium", "edge", "firefox", "opera", "safari", "vivaldi", "whale"], "This list is populated with browsers that yt-dlp supports grabbing cookies from.")

		addSpacer()
		addLabel("Settings for 'SMLD' tab:")
		addButton("Open SMLD logs", lambda: openInBrowser(os.path.join(getBaseConfigDir(),"SMLD","SMLDlog.txt")))
		addDropdownOption("SMLD-mutithreading", "Number of concurrent downloads (EXPERIMENTAL)", [2,4,8,16])
		addDropdownOption("SMLD-source", "Select the media download source", ["YouTube Music", "YouTube"])
		addBooleanOption("SMLD-useytmetadata", "Get metadata from YouTube Music.")

		buttonsFrame = tk.Frame(self.Frame, padx=4, pady=4)
		buttonsFrame.columnconfigure(2, pad=4)
		buttonsFrame.grid(row=2, column=1, columnspan=2, sticky="E")
		self.applyBtn = ttk.Button(buttonsFrame, text="Apply & Save changes", command=lambda: applySettings())
		self.applyBtn.grid(row=1, column=1, sticky="E")
		self.undoBtn = ttk.Button(buttonsFrame, text="Undo", command=lambda: self.loadSettings())
		self.undoBtn.grid(row=1, column=2, sticky="E")






