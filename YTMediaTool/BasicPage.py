import math
import tkinter as tk
import tkinter.font
import tkinter.ttk as ttk
from queue import Empty as QueueEmpty
from Common import openDirInFileBrowser, openFilePicker, createYDLProcess, cleanupYDLTemp
import Info
from Settings import Settings

class Page(tk.Frame):
	def showPage(self):
		self.Frame.bind("<Configure>", lambda event: self.ParentWindow.config(height=event.height+34))
		self.Frame.place(y=34, relwidth=1.0)
		self.ParentWindow.after(1, lambda: self.ParentWindow.config(height=self.Frame.winfo_height()+34))

	def hidePage(self):
		self.Frame.unbind("<Configure>")
		self.Frame.place_forget()

	def __init__(self, window: tk.Tk):
		self.ParentWindow = window

		self.Frame = tk.Frame(window, width=600, height=380, padx=4, pady=4)
		self.Frame.columnconfigure(2, weight=1)

		# URL box
		urlLabel = ttk.Label(self.Frame, text="URL: ")
		urlLabel.grid(row=2, column=1, sticky="E")

		urlInputBoxFrame = tk.Frame(self.Frame)
		urlInputBoxFrame.grid(row=2, column=2, columnspan=2, sticky="WE")
		urlInputBoxFrame.columnconfigure(1, weight=1)

		urlInputBox = ttk.Entry(urlInputBoxFrame)
		urlInputBox.grid(row=1, column=1, sticky="WE")
		urlInputBox.bind("<Control-KeyRelease-a>", lambda _: urlInputBox.select_range(0, tk.END), urlInputBox.icursor(tk.END))
		urlInputBox.bind("<Control-KeyRelease-A>", lambda _: urlInputBox.select_range(0, tk.END), urlInputBox.icursor(tk.END))

		urlInputClearBtn = ttk.Button(urlInputBoxFrame, width=2, padding=0, text="C", command=lambda: urlInputBox.delete(0, 999999))
		urlInputClearBtn.grid(row=1, column=2)

		# File format
		ttk.Label(self.Frame, text="Format: ").grid(row=5, column=1, sticky="E")
		ffFrame = tk.Frame(self.Frame)
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

		dlvideoCheckbox = ttk.Checkbutton(ffFrame, padding=3, text="Video", variable=dlvideo, onvalue=True, offvalue=False, command=dlvideoselection)
		dlvideoCheckbox.grid(row=1, column=2, sticky="W", padx=3)

		dlaudioCheckbox = ttk.Checkbutton(ffFrame, padding=3, text="Audio", variable=dlaudio, onvalue=True, offvalue=False)
		dlaudioCheckbox.grid(row=1, column=3, sticky="W", padx=3)

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

		fileformatDropdown = ttk.OptionMenu(ffFrame, fileformat, next(iter(Info.fileformats)), *Info.fileformats, command=lambda _: ffselection())
		fileformatDropdown.grid(row=1, column=1, sticky="W")

		# Video quality
		vqLabel = ttk.Label(self.Frame, text="Video quality: ")
		vqLabel.grid(row=6, column=1, sticky="E")

		vqDropdown = ttk.OptionMenu(self.Frame, vq, next(iter(Info.videoqualities)), *Info.videoqualities)
		vqDropdown.grid(row=6, column=2, columnspan=2, sticky="W")

		dlvideoselection()
		ffselection()

		# Destination Directory
		ttk.Label(self.Frame, text="Destination directory: ").grid(row=18, column=1, sticky="E")

		dirInputBox = ttk.Entry(self.Frame, textvariable=dirSV)
		dirInputBox.grid(row=18, column=2, sticky="WE")
		dirInputBox.bind("<Control-KeyRelease-a>", lambda _: dirInputBox.select_range(0, tk.END), dirInputBox.icursor(tk.END))
		dirInputBox.bind("<Control-KeyRelease-A>", lambda _: dirInputBox.select_range(0, tk.END), dirInputBox.icursor(tk.END))

		def seldir():
			picked_dir = openFilePicker(window, "openDir", title="Select directory to save downloaded files to...")
			if picked_dir:
				dirSV.set(picked_dir)

		selectDirButton = ttk.Button(self.Frame, text="Browse...", command=seldir)
		selectDirButton.grid(row=18, column=3)

		statusBarSeparator = ttk.Separator(self.Frame, orient="horizontal")
		statusBarSeparator.grid(row=19, column=1, columnspan=3, sticky="WE", pady=4)

		downloadButton = None

		self.modenum = 0
		def downloadf():
			downloadButton.config(state="disabled")

			input2 = urlInputBox.get().strip()

			progressWindow = tk.Toplevel(window)
			progressWindow.resizable(False,False)
			progressWindow.minsize(340, 20)
			progressWindow.columnconfigure(0, minsize=4)
			progressWindow.columnconfigure(2, minsize=4)
			progressWindow.rowconfigure(0, minsize=2)
			progressWindow.rowconfigure(6, minsize=4)
			progressWindow.columnconfigure(1, weight=1)

			pLabel = ttk.Label(progressWindow, text="Preparing download...", font=tk.font.Font(weight="bold"))
			pLabel.grid(row=1, column=1, sticky="W")

			pDownloadedLabel = ttk.Label(progressWindow)
			pDownloadedLabel.grid(row=2, column=1, sticky="W")

			pProgressLabel = ttk.Label(progressWindow)
			pProgressLabel.grid(row=3, column=1, sticky="W")

			pProgressVar = tk.IntVar()
			pProgressBar = ttk.Progressbar(progressWindow, variable=pProgressVar, maximum=100)
			pProgressBar.grid(row=4, column=1, sticky="WE")

			def endFunc(returnStr, r2):
				progressWindow.destroy()

				dText, success = None, False
				if returnStr == "invalidDownloadInput": dText = (self.modenum == 1 and "Blank search term!" or "Invalid URL!")
				elif returnStr == "invalidDirectory": dText = "Invalid destination directory!\nMake sure the path is entered correctly."
				elif returnStr == "pathIsNotDir": dText = "Destination path must be a directory!\nMake sure the path is entered correctly."
				elif returnStr == "noVideoOrAudio": dText = "Neither video nor audio is selected."
				elif returnStr == "success": success = True
				elif returnStr == "unknownException":
					if "Sign in to confirm your age." in str(r2): # FIXME: there's probable a way better method for checking if age-restricted
						dText = "Failed to download:\nVideo is age-restricted."
					elif "HTTP Error 403" in str(r2):
						dText = "Failed to download:\nHTTP Error 403: Forbidden\n\nWait a while and try again later."
					elif "Temporary failure in name resolution" in str(r2):
						dText = "Failed to download:\nTemporary failure in name resolution\n\nAre you connected to the internet?"
					elif "Failed to resolve" in str(r2):
						dText = "Failed to download!\n\nAre you connected to the internet?"
					elif "is not a valid URL" in str(r2):
						dText = "Invalid URL!"
					else:
						dText = "Unknown exception caught during download!\n\n"+str(r2)

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
				if canceled:
					endFunc("canceled", None)
					downloadButton.config(state="normal")
				dataAvailable = returnPipe.poll(0)
				if dataAvailable:
					try:
						rTuple = returnPipe.recv()
						if type(rTuple) == str:
							returnStr, errorStr = rTuple, None
						elif type(rTuple) == tuple:
							returnStr, errorStr = rTuple[0], rTuple[1]
						endFunc(returnStr, errorStr)
						downloadButton.config(state="normal")
					except EOFError:
						# return pipe broken prematurely (most likely just canceled)
						downloadButton.config(state="normal")
				else:
					try:
						dlStatus = statusQueue.get(False)
						pLabel.config(text=dlStatus["progressWindowLabel"])
						if dlStatus["phase"] == "download":
							downloaded_bytes = float(dlStatus["downloaded_bytes"])
							pDownloadedLabel.config(text="Downloaded:")

							if "total_bytes" in dlStatus:
								total_bytes = float(dlStatus["total_bytes"])
								downloadPercent = downloaded_bytes/total_bytes

								pDownloadedLabel.config(text=f"{round(downloaded_bytes/1000000, 2)}MB/{round(total_bytes/1000000, 2)}MB {("total_bytes_is_estimate" in dlStatus and "(estimate) " or "")}downloaded {("speed" in dlStatus and f"at {round(dlStatus["speed"]/1000000, 2)}MB/s" or "")}")
								pProgressLabel.config(text=str(math.floor(downloadPercent*100))+"%")
								pProgressVar.set(math.floor(downloadPercent*100))
							else:
								pDownloadedLabel.config(text=f"{round(downloaded_bytes/1000000, 2)}MB downloaded")
								pProgressLabel.config(text="")
								pProgressVar.set(0)

						else:
							pDownloadedLabel.config(text="")
							pProgressLabel.config(text="")
							pProgressVar.set(0)

					except QueueEmpty:
						pass
					self.Frame.after(100, checkStatus)

			process, returnPipe, statusQueue = createYDLProcess(
				url=(self.modenum == 1 and "ytsearch:"+input2 or input2),
				path=dirSV.get(),
				fileformat=fileformat.get(),
				dlvideo=dlvideo.get(),
				dlaudio=dlaudio.get(),
				videoquality=vq.get()
			)
			process.start()

			self.Frame.after(100, checkStatus)

			canceled = False
			def cancelf():
				pCancelBtn.config(state="disabled")
				nonlocal canceled
				canceled = True
				process.terminate()
				self.Frame.after(200, cleanupYDLTemp)

			pCancelBtn = ttk.Button(progressWindow, text="Cancel", command=cancelf)
			pCancelBtn.grid(row=5, column=1, sticky="E")

			def skip(): pass
			progressWindow.protocol("WM_DELETE_WINDOW", skip)

			progressWindow.grab_set()
			progressWindow.transient(window)
			progressWindow.mainloop()

		downloadButton = ttk.Button(self.Frame, text="Download", command=downloadf)
		downloadButton.grid(row=20, column=1, columnspan=3, sticky="E")

		# Mode
		modeLabel = ttk.Label(self.Frame, text="Mode: ")
		modeLabel.grid(row=1,column=1,sticky="E")

		modes = [
			"Download from URL",
			"Search & Download from YouTube",
		]

		mode = tk.StringVar(value=modes[0])

		urlLabel
		def selection():
			self.modenum = modes.index(mode.get())
			if self.modenum == 0:
				urlLabel.config(text="URL: ")
			elif self.modenum == 1:
				urlLabel.config(text="Search term: ")
		selection()

		modeDropdown = ttk.OptionMenu(self.Frame, mode, modes[0], *modes, command=lambda _: selection())
		modeDropdown.grid(row=1, column=2, columnspan=2, sticky="W")

