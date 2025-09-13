import tkinter as tk
from Common import openFilePicker
from tkinter import messagebox
import os
import os.path
import SMLD
from webbrowser import open_new_tab as openInBrowser
from Common import getBaseConfigDir
from Settings import Settings
import threading
import SMLDprogressTracker

#Website: https://www.tunemymusic.com/transfer

global download
global downloaddirectory
global getprogress
global downloaddirectory1
process1 = None

librarydirfortextbox, download = None, None
downloaddirectory1 = os.path.expanduser("~/YTMediaTool/Downloads/")

progress = 0
rlines = 0
tlines = 0

currentlibrarydirectory = " "
refresher = True
fileformats = {
	'm4a':	{'video': False, 'audio': True, 'ext': "m4a"},
	'mp3':	{'video': False, 'audio': True, 'ext': "mp3"},
	'ogg':	{'video': False, 'audio': True, 'ext': "ogg"},
	'flac':	{'video': False, 'audio': True, 'ext': "flac"},
}

def startthreads():
	global threadnumber
	threadnumber = 0

	threadcount = int(Settings["SMLD-mutithreading"])
	for threadnumber in range(threadcount):

		with open(os.path.join(getBaseConfigDir(),"SMLD", "Temp", "Done" + str(threadnumber) + ".txt"), 'w') as f:
			f.write("0")

		def smld_a():
			SMLD.runsmld(threadnumber)
		#libraryfiledirectory = os.path.join(getBaseConfigDir(),"SMLD", "Temp", "Songlist" + str(threadnumber) + ".txt")
		#with open(libraryfiledirectory, 'r', encoding='utf-8') as tiedosto:
			#rivit = tiedosto.readlines()

		print("Threadcount:" + str(threadnumber))
		smld_b = threading.Thread(target=smld_a)
		smld_b.start()
		print("Thread " + str(threadnumber) + " has been started------------------------------------------------------------------------------------------------------------------")

with open(os.path.join(getBaseConfigDir(),"SMLD", "Temp", "cancel.txt"), "w") as f:
	f.write("0")
	f.close()
def createFrame(window):
	fileformat = tk.StringVar(value=next(iter(fileformats)))
	global frame
	frame = tk.Frame(window, width=600, height=380)
	frame.columnconfigure(2, weight=1)
	def _frame_reconf(event):
		window.config(height=event.height+34)
	global showPage, hidePage, cancel
	def hidePage():
		frame.unbind("<Configure>")
		frame.place_forget()
	def showPage():
		frame.bind("<Configure>", _frame_reconf)
		frame.place(y=34, relwidth=1.0)
		window.after(1, lambda: window.config(height=frame.winfo_height()+34))
	librarydirfortextbox = os.path.expanduser("~/YTMediaTool/")
	print (librarydirfortextbox)

	def seldownloaddir1():
		picked_dir = openFilePicker(window, "openDir")
		if picked_dir:
			downloaddirectory1 = picked_dir
			downloaddirectory2.set(downloaddirectory1)
			print(downloaddirectory1)
			with open(os.path.join(getBaseConfigDir(),"SMLD", "Temp", "downloaddirectory.txt"), "w") as f:
				f.write(downloaddirectory1)
				f.close()
			if not os.path.isfile(os.path.join(downloaddirectory1,"Quick Download.txt")):
				with open(os.path.join(downloaddirectory1,"Quick Download.txt"), "w") as f:
					f.write("CUSTOM DOWNLOAD FORMAT FOR QUICK DOWNLOADS. FORMAT: (SONGNAME, ARTIST), DO NOT REMOVE THIS LINE.")
					f.close()

	def sellibrarydirectory():
		global currentlibrarydirectory
		currentlibrarydirectory = openFilePicker(window, "openFile")
		if currentlibrarydirectory:
			print(currentlibrarydirectory)
			librarydirfortextbox.set(currentlibrarydirectory)

		# Destination Directory
	tk.Label(frame, text="Destination directory: ").grid(row=1, column=1, sticky="W")

	downloaddirectory2 = tk.StringVar()
	downloaddirectory2.set(os.path.expanduser("~/YTMediaTool/Downloads/"))

	dirInputBox = tk.Entry(frame, textvariable=downloaddirectory2)
	dirInputBox.grid(row=1, column=2, sticky="WE")
	dirInputBox.bind("<Control-KeyRelease-a>", lambda _: dirInputBox.select_range(0, tk.END), dirInputBox.icursor(tk.END))
	dirInputBox.bind("<Control-KeyRelease-A>", lambda _: dirInputBox.select_range(0, tk.END), dirInputBox.icursor(tk.END))

	selectDirButton = tk.Button(frame, text="Browse...", command=seldownloaddir1)
	selectDirButton.grid(row=1, column=3)

	tk.Label(frame, text="Library list directory: ").grid(row=2, column=1, sticky="W")
	librarydirfortextbox = tk.StringVar()

	librarydirfortextbox.set("Enter library file directory here.")
	libraryDirInputBox = tk.Entry(frame, textvariable=librarydirfortextbox)
	libraryDirInputBox.grid(row=2, column=2, sticky="WE")
	libraryDirInputBox.bind("<Control-KeyRelease-a>", lambda _: libraryDirInputBox.select_range(0, tk.END), libraryDirInputBox.icursor(tk.END))
	libraryDirInputBox.bind("<Control-KeyRelease-A>", lambda _: libraryDirInputBox.select_range(0, tk.END), libraryDirInputBox.icursor(tk.END))

	selectDirButton = tk.Button(frame, text="Browse...", command=sellibrarydirectory)
	selectDirButton.grid(row=2, column=3)

	openlink = tk.Button(frame, text="Open .csv tool", command=lambda: openInBrowser("https://www.tunemymusic.com/transfer"))
	openlink.grid(row=3, column=2, sticky="W")

	info = tk.Label(frame, text="\n SMLD is a tool designed to download large amounts of audio files from YouTube. Currently it works with iTunes and Spotify playlists. Select .csv files with the library list directory picker and use the .csv tool to make them. Metadata is only added to .m4a files.", wraplength = 500 )
	info.grid(row=8, column=1, columnspan = 3)


	def refresher():
		global threadnumber
		currentlibrarydirectory = os.path.expanduser("~/YTMediaTool/")

		if not os.path.exists(currentlibrarydirectory + "Downloads/"):
			os.makedirs(currentlibrarydirectory + "Downloads/")

		global cancel
		with open(os.path.join(getBaseConfigDir(),"SMLD", "Temp", "cancel.txt"), "r") as f:
			cancel1 = f.read()
			if int(cancel1) == 1:
				print("cancel")
			else:
				with open(os.path.join(getBaseConfigDir(),"SMLD", "Temp", "Done.txt"), "r") as f:
					done = f.read()
					f.close()
					if done == "1":
						SMLDprogressTracker.writecancel()
						print("Done")
				window.after(1000, refresher)
		f.close()

		if os.path.isfile(os.path.join(getBaseConfigDir(),"SMLD", "Temp", "songinfo.txt")):
			with open(os.path.join(getBaseConfigDir(),"SMLD", "Temp", "songinfo.txt"), "r") as f:
				filter = "[]'"
				artist = f.readlines(1)
				for char in filter:
					artist = str(artist).replace(char, "")
					artist = artist.replace("\\n", "")
				songinfo1.config(text="Artist: "+ str(artist))
				song = f.readlines(2)
				for char in filter:
					song = str(song).replace(char, "")
					song = song.replace("\\n", "")
				songinfo2.config(text="Song: "+ str(song))
				album = f.readlines(3)
				for char in filter:
					album = str(album).replace(char, "")
				songinfo3.config(text="Album: "+ str(album))
			f.close()

		if os.path.isfile(os.path.join(getBaseConfigDir(),"SMLD", "Temp", "progress.txt")):
			with open(os.path.join(getBaseConfigDir(),"SMLD", "Temp", "progress.txt"), "r") as f:
				progress = str(f.readlines(1))

				filter2 = "[]'"
				for char in filter2:
					progress = str(progress).replace(char, "")
				progress = progress.replace("\\n", "")
				pg.config(text = "Progress: "+ str(progress) + "%")

				rlines = str(f.readlines(2))
				for char in filter2:
					rlines = str(rlines).replace(char, "")
				rlines = rlines.replace("\\n", "")

				tlines = str(f.readlines(3))
				for char in filter2:
					tlines = str(tlines).replace(char, "")
				tlines = tlines.replace("\\n", "")

				np.config(text =f"  Songs downloaded: {str(rlines)} / {str(tlines)} ")
				f.close()

	def setupSMLD():
		with open(os.path.join(getBaseConfigDir(),"SMLD","SMLDlog.txt"), 'w', encoding='utf-8') as log:
			log.write("")
			log.close()

		number = 0
		while number < 17:
			poistettava = os.path.join(getBaseConfigDir(),"SMLD", "Temp", "Songlist" + str(number) +".txt")
			if os.path.isfile(poistettava):
				os.remove(poistettava)
				print("Removed songlist: "+ str(number))
			number = number + 1

		if os.path.isfile(currentlibrarydirectory):
			downloadb1.config(state="disabled")
			fileformatDropdown.config(state="disabled")
			global process1
			global smld_a

			cancelb.grid(row=1, column=3, sticky="W")
			pg.grid(row=1, column=4)
			np.grid(row=1, column=5)


			with open(os.path.join(getBaseConfigDir(),"SMLD", "Temp", "libraryfiledirectory.txt"), "w") as f:
				f.write(str(currentlibrarydirectory))
				f.close()

			with open(os.path.join(getBaseConfigDir(),"SMLD", "Temp", "cancel.txt"), "w") as f:
				f.write("0")
				f.close()

			with open(os.path.join(getBaseConfigDir(),"SMLD", "Temp", "fileformat.txt"), "w") as f:
				f.write(fileformat.get())
				f.close()

			with open(os.path.join(getBaseConfigDir(),"SMLD", "Temp", "Done.txt"), "w") as f:
				f.write("0")
				f.close()

			window.after(1, refresher)
			threadcount = int(Settings["SMLD-mutithreading"])
			SMLD.setupSMLD(threadcount, str(currentlibrarydirectory))
			songinfo2.grid(row=6, column=1, columnspan = 3, sticky="W")
			songinfo1.grid(row=5, column=1, columnspan = 3, sticky="W")
			songinfo3.grid(row=7, column=1, columnspan = 3, sticky="W")


		else:
			messagebox.showinfo("File not found", "File cannot be found or it doesn't exist. Please enter a valid file path.")

	frame1 = tk.Frame(frame)
	frame1.grid(row=4, column=1, sticky="WE", columnspan=4)	#sticky="W" = tasaus west (ilmansuunnat)  columnspan=2 = monta saraketta grid vie

	fileformatDropdown = tk.OptionMenu(frame1, fileformat, *fileformats)
	fileformatDropdown.grid(row=1, column=2, sticky="W")

	def cancel():
		with open(os.path.join(getBaseConfigDir(),"SMLD", "Temp", "cancel.txt"), "w") as f:
			f.write("1")
			f.close()

		messagebox.showinfo("Done", "Downloading has been completed")

		cancelb.grid_forget()
		downloadb1.config(state="normal")
		fileformatDropdown.config(state="normal")
		pg.grid_forget()
		np.grid_forget()
		songinfo1.grid_forget()
		songinfo2.grid_forget()
		songinfo3.grid_forget()
	cancelb=tk.Button(frame1, text="Cancel", command=cancel)#.grid(row=30, column=0, sticky="E")
	downloadb1 = tk.Button(frame1, text="Download", command=setupSMLD)
	downloadb1.grid(row=1, column=1, sticky="W")

	pg = tk.Label(frame1, text="Progress: "+ str(progress) + "%")
	np = tk.Label(frame1, text=f"Remaining/Total Songs {str(rlines)}/{str(tlines)} ")

	global songinfo1
	songinfo1 = tk.Label(frame, )
	songinfo2 = tk.Label(frame)
	songinfo3 = tk.Label(frame)
