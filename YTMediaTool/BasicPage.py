import math
import tkinter as tk
from queue import Empty as QueueEmpty
from Common import openDirInFileBrowser, openFilePicker, createYDLProcess
import Info
from Settings import Settings

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

	urlInputBoxFrame = tk.Frame(frame)
	urlInputBoxFrame.grid(row=2, column=2, columnspan=2, sticky="WE")
	urlInputBoxFrame.columnconfigure(1, weight=1)

	urlInputBox = tk.Entry(urlInputBoxFrame)
	urlInputBox.grid(row=1, column=1, sticky="WE")
	urlInputBox.bind("<Control-KeyRelease-a>", lambda _: urlInputBox.select_range(0, tk.END), urlInputBox.icursor(tk.END))
	urlInputBox.bind("<Control-KeyRelease-A>", lambda _: urlInputBox.select_range(0, tk.END), urlInputBox.icursor(tk.END))

	urlInputClearBtn = tk.Button(urlInputBoxFrame, text="C", command=lambda: urlInputBox.delete(0, 999999))
	urlInputClearBtn.grid(row=1, column=2)

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
		ff = Info.fileformats[fileformat.get()]
		if "video" in ff and ff["video"] == True:
			dlvideoCheckbox.config(state="normal")
			if dlvideo.get() == True: vqDropdown.grid(row=6, column=2, columnspan=2, sticky="W"); vqLabel.grid(row=6, column=1, sticky="E")
		else:
			dlvideoCheckbox.config(state="disabled")
			vqDropdown.grid_forget(); vqLabel.grid_forget()
		if "warn" in ff:
			tk.messagebox.showwarning("Warning", ff["warn"]) # FIXME make this into a button next to the format dropdown instead of a popup

	fileformatDropdown = tk.OptionMenu(ffFrame, fileformat, *Info.fileformats, command=lambda _: ffselection())
	fileformatDropdown.grid(row=1, column=1, sticky="W")

	# Video quality
	vqLabel = tk.Label(frame, text="Video quality: ")
	vqLabel.grid(row=6, column=1, sticky="E")

	vqDropdown = tk.OptionMenu(frame, vq, *Info.videoqualities)
	vqDropdown.grid(row=6, column=2, columnspan=2, sticky="W")

	# Destination Directory
	tk.Label(frame, text="Destination directory: ").grid(row=19, column=1, sticky="E")

	dirInputBox = tk.Entry(frame, textvariable=dirSV)
	dirInputBox.grid(row=19, column=2, sticky="WE")
	dirInputBox.bind("<Control-KeyRelease-a>", lambda _: dirInputBox.select_range(0, tk.END), dirInputBox.icursor(tk.END))
	dirInputBox.bind("<Control-KeyRelease-A>", lambda _: dirInputBox.select_range(0, tk.END), dirInputBox.icursor(tk.END))

	def seldir():
		picked_dir = openFilePicker(window, "openDir", title="Select directory to save downloaded files to...")
		if picked_dir:
			dirSV.set(picked_dir)

	selectDirButton = tk.Button(frame, text="Browse...", command=seldir)
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
			dataAvailable = returnPipe.poll(0)
			if dataAvailable:
				rTuple = returnPipe.recv()
				returnStr, errorStr = rTuple[0], rTuple[1]
				endFunc(returnStr, errorStr)
				downloadButton.config(state="normal")
			else:
				try:
					dlStatus = statusQueue.get(False)
					pLabel.config(text=dlStatus["progressWindowLabel"])
					if dlStatus["progress"] >= 0:
						pProgressLabel.config(text="Progress: ")
						pProgressAmount.config(text=str(math.floor(dlStatus["progress"]*100))+"%")
					else:
						pProgressLabel.config(text="")
						pProgressAmount.config(text="")
				except QueueEmpty:
					pass
				frame.after(100, checkStatus)

		process, returnPipe, statusQueue = createYDLProcess(
			url=(modenum == 1 and "ytsearch:"+input2 or input2),
			path=dirSV.get(),
			fileformat=fileformat.get(),
			dlvideo=dlvideo.get(),
			dlaudio=dlaudio.get(),
			videoquality=vq.get()
		)
		process.start()

		frame.after(100, checkStatus)

		def skip(): pass
		progressWindow.protocol("WM_DELETE_WINDOW", skip)

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
