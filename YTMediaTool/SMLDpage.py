import PySide6.QtWidgets as qtw
import PySide6.QtGui as qtg
import PySide6.QtCore as qtc
from Common import openFilePicker
import os
import os.path
import SMLD
from Common import getBaseConfigDir
from Settings import Settings
import threading
import SMLDprogressTracker

#Website: https://www.tunemymusic.com/transfer

global download
global downloaddirectory
global getprogress
global downloaddirectory1
global rate
process1 = None

librarydirfortextbox, download = None, None
downloaddirectory1 = os.path.expanduser("~/YTMediaTool/Downloads/")

progress = 0
rlines = 0
tlines = 0
rate = 0

currentlibrarydirectory = " "
refresher = True
fileformats = {
	'm4a':	{'video': False, 'audio': True, 'ext': "m4a"},
	'mp3':	{'video': False, 'audio': True, 'ext': "mp3"},
	'ogg':	{'video': False, 'audio': True, 'ext': "ogg"},
	'flac':	{'video': False, 'audio': True, 'ext': "flac"},
}

def setupfolders():
	if not os.path.exists(os.path.join(getBaseConfigDir(),"SMLD")):
		os.makedirs(os.path.join(getBaseConfigDir(),"SMLD"))

	if not os.path.exists(os.path.join(getBaseConfigDir(),"SMLD", "Temp")):
		os.makedirs(os.path.join(getBaseConfigDir(),"SMLD", "Temp"))

def resetfiles():
	with open(os.path.join(getBaseConfigDir(),"SMLD", "Temp", "progress.txt"), "w") as f:
		f.close()

	with open(os.path.join(getBaseConfigDir(),"SMLD", "Temp", "cancel.txt"), "w") as f:
		f.write("0")
		f.close()

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



class Page(qtw.QWidget):
	def __init__(self, window: qtw.QWidget):
		super().__init__()

		self.layout = qtw.QGridLayout(self)
		self.layout.setColumnStretch(2, 1)

		self.fileformat = next(iter(fileformats))

		global cancel

		self.librarydirfortextbox = os.path.expanduser("~/YTMediaTool/")
		print (self.librarydirfortextbox)

		def seldownloaddir1():
			setupfolders()
			picked_dir = openFilePicker(window, "openDir")
			if picked_dir:
				downloaddirectory1 = picked_dir
				self.downloaddirectory2 = downloaddirectory1
				dirInputBox.setText(downloaddirectory1)
				print(downloaddirectory1)
				with open(os.path.join(getBaseConfigDir(),"SMLD", "Temp", "downloaddirectory.txt"), "w") as f:
					f.write(downloaddirectory1)
					f.close()
				if not os.path.isfile(os.path.join(downloaddirectory1,"Quick Download.txt")):
					with open(os.path.join(downloaddirectory1,"Quick Download.txt"), "w") as f:
						f.write("CUSTOM DOWNLOAD FORMAT FOR QUICK DOWNLOADS. FORMAT: (ARTIST,SONG1,SONG2,SONG3...), DO NOT REMOVE THIS LINE.")
						f.close()

		def sellibrarydirectory():
			setupfolders()
			global currentlibrarydirectory
			currentlibrarydirectory = openFilePicker(window, "openFile")
			if currentlibrarydirectory:
				print(currentlibrarydirectory)
				libraryDirInputBox.setText(currentlibrarydirectory)

			# Destination Directory
		self.layout.addWidget(qtw.QLabel(self, text="Destination directory: "), 1, 1, 1, 1, qtc.Qt.AlignmentFlag.AlignRight)

		self.downloaddirectory2 = os.path.expanduser("~/YTMediaTool/Downloads/")

		dirInputBox = qtw.QLineEdit(self, text=self.downloaddirectory2, enabled=False)
		def dirInputBoxEdited(val):
			self.downloaddirectory2 = val
		dirInputBox.textChanged.connect(dirInputBoxEdited)
		self.layout.addWidget(dirInputBox, 1, 2)

		selectDirButton = qtw.QToolButton(self, text="Browse...", icon=qtg.QIcon.fromTheme(qtg.QIcon.ThemeIcon.FolderOpen), toolTip="Browse...")
		selectDirButton.clicked.connect(seldownloaddir1)
		self.layout.addWidget(selectDirButton, 1, 3)

		self.layout.addWidget(qtw.QLabel(self, text="Library list file: "), 2, 1, 1, 1, qtc.Qt.AlignmentFlag.AlignRight)
		self.librarydirfortextbox = ""

		def librarydirfortextboxchanged(val):
			self.librarydirfortextbox = str(val)

		libraryDirInputBox = qtw.QLineEdit(self, placeholderText="Enter library file path here.")
		libraryDirInputBox.textChanged.connect(librarydirfortextboxchanged)
		self.layout.addWidget(libraryDirInputBox, 2, 2)

		selectDirButton = qtw.QToolButton(self, text="Browse...", icon=qtg.QIcon.fromTheme(qtg.QIcon.ThemeIcon.DocumentOpen), toolTip="Browse...")
		selectDirButton.clicked.connect(sellibrarydirectory)
		self.layout.addWidget(selectDirButton, 2, 3)

		openlink = qtw.QPushButton(self, text="Open .csv tool")
		openlink.clicked.connect(lambda: qtg.QDesktopServices.openUrl("https://www.tunemymusic.com/transfer"))
		self.layout.addWidget(openlink, 3, 2, 1, 1, qtc.Qt.AlignmentFlag.AlignRight)

		info = qtw.QLabel(self, text="\n SMLD is a tool designed to download small and large amounts of audio files from YouTube and YouTube Music. Select library files with the library list directory picker and use the .csv tool or Quick Download format to make them. Metadata is only added to .m4a files. Quick download format can be used to add metadata to .m4a files. See GitHub page for more information.", wordWrap=True)
		self.layout.addWidget(info, 8, 1, 1, 3)

		def refresher():
			if SMLD.filenotfound:
				qtw.QMessageBox.critical(window, "File not found", "File cannot be found. See the log for more information.")
				SMLD.filenotfound = False

			if SMLD.smlderror:
				qtw.QMessageBox.critical(window, "ERROR", "An error occured. See the log for more information.")
				SMLD.smlderror = False

			if SMLD.ratelimited:
				qtw.QMessageBox.critical(window, "Rate limited!", "You have been rate limited! Try to enable cookies!")
				SMLD.ratelimited = False

			if SMLD.failalert:
				qtw.QMessageBox.critical(window, "Download failed!", "Download has failed for over 10 times! Try updating yt-dlp and YTMediaTool!")
				SMLD.failalert = False

			currentlibrarydirectory = os.path.expanduser("~/YTMediaTool/")

			if not os.path.exists(currentlibrarydirectory + "Downloads/"):
				os.makedirs(currentlibrarydirectory + "Downloads/")

			with open(os.path.join(getBaseConfigDir(),"SMLD", "Temp", "Done.txt"), "r") as f:
				done = f.read()
				f.close()
				if done == "1":
					qtw.QMessageBox.information(window, "Done", "Downloading has been completed")

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

					self.refresherTimer.start(1000)
			f.close()

			if os.path.isfile(os.path.join(getBaseConfigDir(),"SMLD", "Temp", "songinfo.txt")):
				with open(os.path.join(getBaseConfigDir(),"SMLD", "Temp", "songinfo.txt"), "r") as f:
					filter = "[]'"
					artist = f.readlines(1)
					for char in filter:
						artist = str(artist).replace(char, "")
						artist = artist.replace("\\n", "")
					songinfo1.setText("Artist: "+ str(artist))
					song = f.readlines(2)
					for char in filter:
						song = str(song).replace(char, "")
						song = song.replace("\\n", "")
					songinfo2.setText("Song: "+ str(song))
					album = f.readlines(3)
					for char in filter:
						album = str(album).replace(char, "")
					songinfo3.setText("Album: "+ str(album))
				f.close()

			if os.path.isfile(os.path.join(getBaseConfigDir(),"SMLD", "Temp", "progress.txt")):
				with open(os.path.join(getBaseConfigDir(),"SMLD", "Temp", "progress.txt"), "r") as f:
					progress = str(f.readlines(1))

					filter2 = "[]/',"
					for char in filter2:
						progress = str(progress).replace(char, "")
					progress = progress.replace("\\n", "")
					pg.setText("Progress: "+ str(progress) + "%")

					rlines = str(f.readlines(2))
					for char in filter2:
						rlines = str(rlines).replace(char, "")
					rlines = rlines.replace("\\n", "")

					tlines = str(f.readlines(3))
					for char in filter2:
						tlines = str(tlines).replace(char, "")
					tlines = tlines.replace("\\n", "")

					np.setText(f"  Songs downloaded: {str(rlines)} / {str(tlines)} ")
					f.close()

			if os.path.isfile(os.path.join(getBaseConfigDir(),"SMLD", "Temp", "rate.txt")):
				with open(os.path.join(getBaseConfigDir(),"SMLD", "Temp", "rate.txt"), "r") as f:
					rate = str(f.readlines(1))
				filter2 = "[]'"
				for char in filter2:
					rate = str(rate).replace(char, "")
				rate = rate.replace("\\n", "")
				rd.setText("Rate is: "+ str(rate) + " SPM")

		def setupSMLD():
			resetfiles()
			number = 0
			while number < 17:
				poistettava = os.path.join(getBaseConfigDir(),"SMLD", "Temp", "Songlist" + str(number) +".txt")
				if os.path.isfile(poistettava):
					os.remove(poistettava)
					print("Removed songlist: "+ str(number))
				number = number + 1

			if os.path.isfile(currentlibrarydirectory):
				downloadb1.setEnabled(False)
				fileformatDropdown.setEnabled(False)

				cancelb.setVisible(True)
				pg.setVisible(True)
				np.setVisible(True)
				rd.setVisible(True)


				with open(os.path.join(getBaseConfigDir(),"SMLD", "Temp", "libraryfiledirectory.txt"), "w") as f:
					f.write(str(currentlibrarydirectory))
					f.close()

				with open(os.path.join(getBaseConfigDir(),"SMLD", "Temp", "cancel.txt"), "w") as f:
					f.write("0")
					f.close()

				with open(os.path.join(getBaseConfigDir(),"SMLD", "Temp", "fileformat.txt"), "w") as f:
					f.write(self.fileformat)
					f.close()

				with open(os.path.join(getBaseConfigDir(),"SMLD", "Temp", "Done.txt"), "w") as f:
					f.write("0")
					f.close()

				self.refresherTimer.start(1)
				threadcount = int(Settings["SMLD-mutithreading"])
				SMLD.setupSMLD(threadcount, str(currentlibrarydirectory))
				songinfo2.setVisible(True)
				songinfo1.setVisible(True)
				songinfo3.setVisible(True)


			else:
				qtw.QMessageBox.warning(self, "File not found", "File cannot be found or it doesn't exist. Please enter a valid file path.")

		self.refresherTimer = qtc.QTimer(self, singleShot=True)
		self.refresherTimer.timeout.connect(refresher)

		frame1 = qtw.QFrame(self)
		self.layout.addWidget(frame1, 4, 1, 1, 4)	#kuudes parametry jätettynä tyhjäksi venyttää widgetin viemään koko solun tilan     viides parametri = monta saraketta grid vie
		frame1layout = qtw.QHBoxLayout(frame1)
		frame1layout.setContentsMargins(0,0,0,0)

		fileformatDropdown = qtw.QComboBox(frame1)
		fileformatDropdown.addItems(fileformats.keys())
		frame1layout.addWidget(fileformatDropdown)

		def cancel():
			with open(os.path.join(getBaseConfigDir(),"SMLD", "Temp", "cancel.txt"), "w") as f:
				f.write("1")
				f.close()

			cancelb.setVisible(False)
			downloadb1.setEnabled(True)
			fileformatDropdown.setEnabled(True)
			pg.setVisible(False)
			np.setVisible(False)
			rd.setVisible(False)
			songinfo1.setVisible(False)
			songinfo2.setVisible(False)
			songinfo3.setVisible(False)
		cancelb=qtw.QPushButton(frame1, text="&Cancel", visible=False)#.grid(row=30, column=0, sticky="E")
		cancelb.clicked.connect(cancel)
		downloadb1 = qtw.QPushButton(frame1, text="&Download")
		downloadb1.clicked.connect(setupSMLD)
		frame1layout.addWidget(downloadb1)
		frame1layout.addWidget(cancelb)

		pg = qtw.QLabel(frame1, text="Progress: "+ str(progress) + "%", visible=False)
		frame1layout.addWidget(pg)

		np = qtw.QLabel(frame1, text=f"Remaining/Total Songs {str(rlines)}/{str(tlines)} ", visible=False)
		frame1layout.addWidget(np)

		rd = qtw.QLabel(frame1, text="Rate: "+ str(rate) + " SPM", visible=False)
		frame1layout.addWidget(rd)

		frame1layout.addStretch(1)

		global songinfo1
		songinfo1 = qtw.QLabel(self, visible=False)
		self.layout.addWidget(songinfo1, 5, 1, 1, 3)
		songinfo2 = qtw.QLabel(self, visible=False)
		self.layout.addWidget(songinfo2, 6, 1, 1, 3)
		songinfo3 = qtw.QLabel(self, visible=False)
		self.layout.addWidget(songinfo3, 7, 1, 1, 3)

		self.layout.setRowStretch(9, 1)
