import os, math
import tkinter as tk
import threading
from yt_dlp import YoutubeDL
from Common import getUserDownloadDir, openDirInFileBrowser, openFilePicker
from Settings import Settings

fileformats = {
	'Original':	{'video': True, 'audio': True},
	'MP4':	{'video': True, 'audio': True, 'ext': "mp4"},
	'M4A':	{'video': False, 'audio': True, 'ext': "m4a"},
	'WebM':	{'video': True, 'audio': True, 'ext': "webm"},
	'MP3':	{'video': False, 'audio': True, 'ext': "mp3"},
	'Ogg':	{'video': False, 'audio': True, 'ext': "ogg"},
	'FLAC':	{'video': False, 'audio': True, 'ext': "flac", 'warn': "Downloading to FLAC does not magically make your audio high-quality, as audio is almost always converted from a lossy format to this!"},
	'WAV':	{'video': False, 'audio': True, 'ext': "wav", 'warn': "WAV files are uncompressed and will result in very large files! Use with caution."},
	'Theora (ogv)':	{'video': True, 'audio': True, 'ext': "ogv"},
	'Matroska (mkv)':	{'video': True, 'audio': True, 'ext': "mkv"},
	'QuickTime Movie (mov)':	{'video': True, 'audio': True, 'ext': "mov"}
}

videoqualities = {
	'Source': {},
	'2160p (4K)': {'res': 2160},
	'1440p': {'res': 1440},
	'1080p (FHD)': {'res': 1080},
	'720p': {'res': 720},
	'480p': {'res': 480},
	'360p': {'res': 360},
	'288p': {'res': 288},
	'240p': {'res': 240},
	'144p': {'res': 144},
	'72p': {'res': 72}
}

dlStatus = {
	'downloading': False,
	'progressWindowLabel': "",
	'progress': 0,
	'returnStr': None,
	'errorStr': None
}

def download(
	mode: str,
	downloadInput: str,
	directory: str,
	inputff: str,
	inputvq: str,
	dlvideo: bool,
	dlaudio: bool
):
	global dlStatus
	dlStatus["returnStr"] = None
	dlStatus["errorStr"] = None
	dlStatus["progressWindowLabel"] = "Preparing download..."
	dlStatus["progress"] = 0

	print(f"Downloading '{downloadInput}' to '{directory}'...")
	if len(downloadInput) <= 0: print("Invalid download input"); dlStatus["returnStr"] = "invalidDownloadInput"; return
	if len(directory) <= 0 and os.path.exists(directory): print("Invalid directory"); dlStatus["returnStr"] = "invalidDirectory"; return
	if not os.path.isdir(directory): print("Path does not point to a directory!"); dlStatus["returnStr"] = "pathIsNotDir"; return
	if not inputff in fileformats: print("Invalid fileformat"); dlStatus["returnStr"] = "invalidff"; return
	if not inputvq in videoqualities: print("Invalid video quality"); dlStatus["returnStr"] = "invalidvq"; return

	ff = fileformats[inputff]
	vq = videoqualities[inputvq]

	def progress_hook(d):
		try:
			if d['status'] == "downloading":
				downloadPercent = d['downloaded_bytes']/(d['total_bytes'] or 1)
				dlStatus["progressWindowLabel"] = "Downloading..."
				dlStatus["progress"] = math.floor(downloadPercent*100)/100
		except Exception as err:
			print("Error in progress hook:\n"+str(err))

	opts = {
		'verbose': False,
		'outtmpl': {'default': f"{directory}/%(title)s [%(id)s].%(ext)s"},
		'progress_hooks': [progress_hook]
	}

	if ff["video"] == False: dlvideo = False
	if ff["audio"] == False: dlaudio = False

	if "FFmpeg_path" in Settings:
		opts["ffmpeg_location"] = Settings["FFmpeg_path"]

	if dlvideo and dlaudio:
		opts["format"] = "bv*+ba/b"
	elif dlvideo and not dlaudio:
		opts["format"] = "bv"
	elif not dlvideo and dlaudio:
		opts["format"] = "ba"
	else:
		print("No video or audio selected")
		dlStatus["returnStr"] = "noVideoOrAudio"; return

	if "ext" in ff:
		ext = ff["ext"]
		opts['final_ext'] = ext
		opts['postprocessors'] = [{'key': 'FFmpegVideoConvertor', 'preferedformat': ext}]

	if dlvideo and "res" in vq:
		print(f'res:{vq["res"]}')
		opts['format_sort'] = [f'res:{vq["res"]}']

	if mode == "url":
		url = downloadInput
	elif mode == "ytsearch":
		url = f"ytsearch:{downloadInput}"
	else:
		print("Invalid mode")
		dlStatus["returnStr"] = "invalidMode"
		return

	with YoutubeDL(opts) as ydl:
		try:
			c = ydl.download(url)
			print("return code: " + str(c))
			dlStatus["returnStr"] = "success"; return
		except Exception as err:
			print("--- Exception in ydl.download() ---\n"+str(err))
			dlStatus["errorStr"] = str(err)
			dlStatus["returnStr"] = "unknownException"
			return
			# return "unknownException", err

def createFrame(window):
	global frame
	frame = tk.Frame(window, width=600, height=380)
	frame.columnconfigure(2, weight=1)

	global pageOpenedOnce
	pageOpenedOnce = False
	def showPageFirstTime():
		if Settings["BasicPage-DLVideo"] == True:
			dlvideoCheckbox.select()
		if Settings["BasicPage-DLAudio"] == True:
			dlaudioCheckbox.select()
		dlvideoselection()
		ffselection()
		global pageOpenedOnce
		pageOpenedOnce = True

	global showPage, hidePage
	def hidePage():
		frame.place_forget()
	def showPage():
		frame.place(y=34, h=-34, relwidth=1.0, relheight=1.0)
		if not pageOpenedOnce: showPageFirstTime()

	# URL box
	urlLabel = tk.Label(frame, text="URL: ")
	urlLabel.grid(row=2, column=1, sticky="E")

	urlInputBox = tk.Entry(frame)
	urlInputBox.grid(row=2, column=2, columnspan=2, sticky="WE")

	# File format
	tk.Label(frame, text="Format: ").grid(row=5, column=1, sticky="E")
	ffFrame = tk.Frame(frame)
	ffFrame.grid(row=5, column=2, columnspan=2, sticky="W")

	dlvideo = tk.BooleanVar(value=Settings["BasicPage-DLVideo"])
	dlaudio = tk.BooleanVar(value=Settings["BasicPage-DLAudio"])
	fileformat = tk.StringVar(value=Settings["BasicPage-Format"])
	vq = tk.StringVar(value=Settings["BasicPage-VideoQuality"])
	dirSV = tk.StringVar(value=Settings["BasicPage-DownloadDir"])

	def onSaveableSettingUpdate():
		Settings["BasicPage-DLVideo"] = bool(dlvideo.get())
		Settings["BasicPage-DLAudio"] = bool(dlaudio.get())
		Settings["BasicPage-Format"] = str(fileformat.get())
		Settings["BasicPage-VideoQuality"] = str(vq.get())
		Settings["BasicPage-DownloadDir"] = str(dirSV.get())

	dlvideo.trace('w',lambda _, _2, _3: onSaveableSettingUpdate())
	dlaudio.trace('w',lambda _, _2, _3: onSaveableSettingUpdate())
	fileformat.trace('w',lambda _, _2, _3: onSaveableSettingUpdate())
	vq.trace('w',lambda _, _2, _3: onSaveableSettingUpdate())
	dirSV.trace('w',lambda _, _2, _3: onSaveableSettingUpdate())

	def dlvideoselection():
		if dlvideo.get() == True: vqDropdown.grid(row=6, column=2, columnspan=2, sticky="W"); vqLabel.grid(row=6, column=1, sticky="E")
		else: vqDropdown.grid_forget(); vqLabel.grid_forget()

	dlvideoCheckbox = tk.Checkbutton(ffFrame, text="Video", variable=dlvideo, onvalue=True, offvalue=False, command=dlvideoselection)
	dlvideoCheckbox.grid(row=1, column=2, sticky="W")

	dlaudioCheckbox = tk.Checkbutton(ffFrame, text="Audio", variable=dlaudio, onvalue=True, offvalue=False)
	dlaudioCheckbox.grid(row=1, column=3, sticky="W")

	def ffselection():
		ff = fileformats[fileformat.get()]
		if "video" in ff and ff["video"] == True:
			dlvideoCheckbox.config(state="normal")
			if dlvideo.get() == True: vqDropdown.grid(row=6, column=2, columnspan=2, sticky="W"); vqLabel.grid(row=6, column=1, sticky="E")
		else:
			dlvideoCheckbox.config(state="disabled")
			vqDropdown.grid_forget(); vqLabel.grid_forget()
		if "warn" in ff:
			tk.messagebox.showwarning("Warning", ff["warn"]) # FIXME make this into a button next to the format dropdown instead of a popup

	fileformatDropdown = tk.OptionMenu(ffFrame, fileformat, *fileformats, command=lambda _: ffselection())
	fileformatDropdown.grid(row=1, column=1, sticky="W")

	# Video quality
	vqLabel = tk.Label(frame, text="Video quality: ")
	vqLabel.grid(row=6, column=1, sticky="E")
	vqDropdown = tk.OptionMenu(frame, vq, *videoqualities)
	vqDropdown.grid(row=6, column=2, columnspan=2, sticky="W")

	# Destination Directory
	tk.Label(frame, text="Destination directory: ").grid(row=19, column=1, sticky="E")

	dirInputBox = tk.Entry(frame, textvariable=dirSV)
	dirInputBox.grid(row=19, column=2, sticky="WE")

	def seldir():
		picked_dir = openFilePicker(window, "openDir", title="Select directory to save downloaded files to...")
		if picked_dir:
			dirSV.set(picked_dir)

	selectDirButton = tk.Button(frame, text="Pick...", command=seldir)
	selectDirButton.grid(row=19, column=3)

	downloadButton = None

	global modenum
	modenum = 0
	def downloadf():
		downloadButton.config(state="disabled")

		input2 = urlInputBox.get().strip()

		progressWindow = tk.Toplevel(window)
		progressWindow.geometry("360x40")
		progressWindow.resizable(False,False)
		progressWindow.minsize(360, 40)

		progressWindow.rowconfigure(1, weight=1)
		progressWindow.columnconfigure(2, weight=1)

		pLabel = tk.Label(progressWindow, text="Preparing download...")
		pLabel.grid(row=1, column=1, columnspan=2)

		pProgressLabel = tk.Label(progressWindow, text="Progress: ")
		pProgressLabel.grid(row=2, column=1, sticky="E")

		pProgressAmount = tk.Label(progressWindow, text="0%")
		pProgressAmount.grid(row=2, column=2, sticky="W")

		def endFunc(returnStr, r2):
			progressWindow.destroy()

			dText, success = None, False
			if returnStr == "invalidDownloadInput": dText = mode.get() == 1 and "Invalid search term!" or "Invalid URL!"
			elif returnStr == "invalidDirectory": dText = "Invalid destination directory!\nMake sure the path is entered correctly."
			elif returnStr == "pathIsNotDir": dText = "Destination directory must be a directory!"
			elif returnStr == "noVideoOrAudio": dText = "Neither video nor audio is selected."
			elif returnStr == "success": success = True
			elif returnStr == "unknownException":
				if "Sign in to confirm your age." in str(r2): # FIXME: there's probable a way better method for checking if age-restricted
					dText = "Failed to download:\nVideo is age-restricted."
				else:
					dText = "Unknown exception caught while downloading.\n"+str(r2)

			if dText:
				window.update()
				tk.messagebox.showerror("Download error", dText)
			elif success:
				window.update()
				print("Download success!")
				if Settings["BasicPage-ShowDialogAfterDLSuccess"] == True:
					answer = tk.messagebox.askyesno("Download finished", "Download finished.\nOpen destination directory?")
					if answer == True:
						openDirInFileBrowser(dirSV.get())

		def checkStatus():
			if type(dlStatus["returnStr"]) == str:
				returnStr = str(dlStatus["returnStr"])
				errorStr = str(dlStatus["errorStr"])
				dlStatus["returnStr"] = None
				dlStatus["errorStr"] = None
				endFunc(returnStr, errorStr)
				downloadButton.config(state="normal")
			else:
				pLabel.config(text=dlStatus["progressWindowLabel"])
				pProgressAmount.config(text=str(math.floor(dlStatus["progress"]*100))+"%")
				frame.after(100, checkStatus)

		dlThread = threading.Thread(target=download, kwargs={
			'mode': (modenum == 1 and "ytsearch" or "url"),
			'downloadInput': input2,
			'directory': dirSV.get(),
			'inputff': fileformat.get(),
			'inputvq': vq.get(),
			'dlvideo': dlvideo.get(),
			'dlaudio': dlaudio.get()
		})
		dlThread.start()

		frame.after(100, checkStatus)

		progressWindow.grab_set()
		progressWindow.transient(window)
		progressWindow.mainloop()

	downloadButton = tk.Button(frame, text="Download", command=downloadf)
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

