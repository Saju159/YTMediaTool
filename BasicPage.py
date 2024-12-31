import tkinter as tk
from yt_dlp import YoutubeDL
from Common import getUserDownloadDir, openFilePicker

fileformats = {
	'Best':	{'video': True, 'audio': True},
	'mp4':	{'video': True, 'audio': True, 'ext': "mp4"},
	'm4a':	{'video': False, 'audio': True, 'ext': "m4a"},
	'webm':	{'video': True, 'audio': True, 'ext': "webm"},
	'mp3':	{'video': False, 'audio': True, 'ext': "mp3"},
	'ogg':	{'video': False, 'audio': True, 'ext': "ogg"},
	'flac':	{'video': False, 'audio': True, 'ext': "flac"},
	'ogv':	{'video': True, 'audio': True, 'ext': "ogv"},
	'mkv':	{'video': True, 'audio': True, 'ext': "mkv"},
	'mov':	{'video': True, 'audio': True, 'ext': "mov"}
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

def download(
	mode: str,
	downloadInput: str,
	directory: str,
	inputff: str,
	inputvq: str,
	dlvideo: bool,
	dlaudio: bool
):
	print(f"Downloading '{downloadInput}' to '{directory}'...")
	if len(mode) <= 0 or len(downloadInput) <= 0 or len(directory) <= 0 or len(inputff) <= 0: print("Invalid args"); return

	ff = fileformats[inputff]
	vq = videoqualities[inputvq]

	opts = {
		'verbose': False,
		'outtmpl': {'default': f"{directory}/%(title)s [%(id)s].%(ext)s"},
	}

	if dlvideo and dlaudio:
		opts["format"] = "bv*+ba/b"
	elif dlvideo and not dlaudio:
		opts["format"] = "bv"
	elif not dlvideo and dlaudio:
		opts["format"] = "ba"
	else:
		print("No video or audio selected")
		return


	if "ext" in ff:
		ext = ff["ext"]
		opts['final_ext'] = ext,
		opts['postprocessors'] = [{'key': 'FFmpegVideoConvertor', 'preferedformat': ext}]

	if "res" in vq:
		print(inputvq)
		print("test test")
		print(f'res:{vq["res"]}')
		opts['format_sort'] = [f'res:{vq["res"]}']

	if mode == "url":
		url = downloadInput
	elif mode == "ytsearch":
		url = f"ytsearch:{url}"
	else:
		print("Invalid mode"); return

	with YoutubeDL(opts) as ydl:
		c = ydl.download(url)
		print("return code: " + str(c))

def createFrame(window):
	global frame
	frame = tk.Frame(window, width=600, height=380)
	frame.columnconfigure(2, weight=1)

	global pageOpenedOnce
	pageOpenedOnce = False
	def showPageFirstTime():
		dlvideoCheckbox.select() # set checkbuttons to selected here because it wouldn't work if the page wasn't visible
		dlaudioCheckbox.select()
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

	dlvideo = tk.BooleanVar()
	dlaudio = tk.BooleanVar()
	fileformat = tk.StringVar(value=next(iter(fileformats)))

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

	fileformatDropdown = tk.OptionMenu(ffFrame, fileformat, *fileformats, command=lambda _: ffselection())
	fileformatDropdown.grid(row=1, column=1, sticky="W")

	# Video quality
	vqLabel = tk.Label(frame, text="Video quality: ")
	vqLabel.grid(row=6, column=1, sticky="E")
	vq = tk.StringVar(value=next(iter(videoqualities)))
	vqDropdown = tk.OptionMenu(frame, vq, *videoqualities)
	vqDropdown.grid(row=6, column=2, columnspan=2, sticky="W")

	# Destination Directory
	tk.Label(frame, text="Destination directory: ").grid(row=19, column=1, sticky="E")

	dirSV = tk.StringVar()
	dirSV.set(getUserDownloadDir())

	dirInputBox = tk.Entry(frame, textvariable=dirSV)
	dirInputBox.grid(row=19, column=2, sticky="WE")

	def seldir():
		picked_dir = openFilePicker(window, "openDir", title="Select directory to save downloaded files to...")
		if picked_dir:
			dirSV.set(picked_dir)

	selectDirButton = tk.Button(frame, text="Pick...", command=seldir)
	selectDirButton.grid(row=19, column=3)

	global modenum
	modenum = 0
	def downloadf():
		input2 = urlInputBox.get().strip()
		download(
			mode = (modenum == 1 and "ytsearch" or "url"),
			downloadInput = input2,
			directory = dirSV.get(),
			inputff = fileformat.get(),
			inputvq = vq.get(),
			dlvideo = dlvideo.get(),
			dlaudio = dlaudio.get()
		)

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

