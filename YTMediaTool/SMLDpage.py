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
global done
global progresstoshow, remainingtoshow, totaltoshow
progresstoshow =  ""
remainingtoshow = ""
totaltoshow = ""

process1 = None
done = False

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

def readfile(path):
	with open(path, "r", encoding='utf-8') as file:
		value = file.read()

		return value

def writefile(path, data):
	with open(path, "w", encoding='utf-8') as file:
		file.write(data)

def setupfolders():
	if not os.path.exists(os.path.join(getBaseConfigDir(),"SMLD")):
		os.makedirs(os.path.join(getBaseConfigDir(),"SMLD"))

	if not os.path.exists(os.path.join(getBaseConfigDir(),"SMLD", "Temp")):
		os.makedirs(os.path.join(getBaseConfigDir(),"SMLD", "Temp"))

def resetfiles():
	SMLD.cancel = False

def startthreads():
	global threadnumber
	threadnumber = 0

	threadcount = int(Settings["SMLD-mutithreading"])
	for threadnumber in range(threadcount):

		SMLD.donelist[threadnumber] = False

		def smld_a():
			SMLD.runsmld(threadnumber)

		print("Threadcount:" + str(threadnumber))
		smld_b = threading.Thread(target=smld_a)
		smld_b.start()
		print("Thread " + str(threadnumber) + " has been started------------------------------------------------------------------------------------------------------------------")



class Page(qtw.QWidget):
	def __init__(self, window: qtw.QWidget):
		super().__init__()

		def showerror(title, body):
			qtw.QMessageBox.warning(self, title, body)

		self.layout = qtw.QGridLayout(self)
		self.layout.setColumnStretch(2, 1)

		self.fileformat = next(iter(fileformats))

		global cancel

		self.librarydirfortextbox = os.path.expanduser("~/YTMediaTool/")
		print (self.librarydirfortextbox)

		SMLD.downloaddirectory = downloaddirectory1
		def seldownloaddir1():
			setupfolders()
			picked_dir = openFilePicker(window, "openDir")
			if picked_dir:
				writefile(os.path.join(getBaseConfigDir(),"SMLD", "Temp","downloaddir.txt"), picked_dir)
				downloaddirectory1 = picked_dir
				self.downloaddirectory2 = downloaddirectory1
				dirInputBox.setText(downloaddirectory1)
				print(downloaddirectory1)
				SMLD.downloaddirectory = downloaddirectory1
				if not os.path.isfile(os.path.join(downloaddirectory1,"Quick Download.txt")):
					with open(os.path.join(downloaddirectory1,"Quick Download.txt"), "w", encoding='utf-8') as f:
						f.write("CUSTOM DOWNLOAD FORMAT FOR QUICK DOWNLOADS. FORMAT: (ARTIST,SONG1,SONG2,SONG3...), DO NOT REMOVE THIS LINE.")
						f.close()

		def sellibrarydirectory():
			setupfolders()
			global currentlibrarydirectory
			currentlibrarydirectory = openFilePicker(window, "openFile")
			if currentlibrarydirectory:
				writefile(os.path.join(getBaseConfigDir(),"SMLD", "Temp","librarydir.txt"), currentlibrarydirectory)
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
		if os.path.isfile(os.path.join(getBaseConfigDir(),"SMLD", "Temp","downloaddir.txt")):
			downloaddir2 = readfile(os.path.join(getBaseConfigDir(),"SMLD", "Temp","downloaddir.txt")).strip()
			SMLD.downloaddirectory = downloaddir2
			dirInputBox.setText(downloaddir2)


		selectDirButton = qtw.QToolButton(self, text="Browse...", icon=qtg.QIcon.fromTheme(qtg.QIcon.ThemeIcon.FolderOpen), toolTip="Browse...")
		selectDirButton.clicked.connect(seldownloaddir1)
		self.layout.addWidget(selectDirButton, 1, 3)

		self.layout.addWidget(qtw.QLabel(self, text="Library list file or playlist link: "), 2, 1, 1, 1, qtc.Qt.AlignmentFlag.AlignRight)
		self.librarydirfortextbox = ""

		def librarydirfortextboxchanged(val):
			self.librarydirfortextbox = str(val)

		libraryDirInputBox = qtw.QLineEdit(self, placeholderText="Enter library file path or playlist link here.", clearButtonEnabled=True)
		libraryDirInputBox.textChanged.connect(librarydirfortextboxchanged)
		self.layout.addWidget(libraryDirInputBox, 2, 2)

		if os.path.isfile(os.path.join(getBaseConfigDir(),"SMLD", "Temp","librarydir.txt")):
			librarydir2 = readfile(os.path.join(getBaseConfigDir(),"SMLD", "Temp","librarydir.txt")).strip()
			libraryDirInputBox.setText(librarydir2)

		selectDirButton = qtw.QToolButton(self, text="Browse...", icon=qtg.QIcon.fromTheme(qtg.QIcon.ThemeIcon.DocumentOpen), toolTip="Browse...")
		selectDirButton.clicked.connect(sellibrarydirectory)
		self.layout.addWidget(selectDirButton, 2, 3)

		openlink = qtw.QPushButton(self, text="Open .csv tool")
		openlink.clicked.connect(lambda: qtg.QDesktopServices.openUrl("https://www.tunemymusic.com/transfer"))
		self.layout.addWidget(openlink, 3, 2, 1, 1, qtc.Qt.AlignmentFlag.AlignRight)

		info = qtw.QLabel(self, text="\nSMLD is a tool designed to download small and large amounts of audio files from YouTube Music and Spotify. Enter a playlist link to the second text field or input a .txt containing a list of the songs you want to download. Metadata is only added to .m4a files. See GitHub page for more information and a more complete feature list.", wordWrap=True)
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
			
			if SMLD.ytprivate:
				qtw.QMessageBox.critical(window, "Download playlist failed!", "Error downloading playlist! Is the playlist private?")
				SMLD.ytprivate = False

			currentlibrarydirectory = os.path.expanduser("~/YTMediaTool/")

			if not os.path.exists(currentlibrarydirectory + "Downloads/"):
				os.makedirs(currentlibrarydirectory + "Downloads/")

			if done:
				qtw.QMessageBox.information(window, "Done", "Downloading has been completed")

			if SMLD.cancel:
				print("cancel")
			else:
				self.refresherTimer.start(1000)
			if done:
				SMLDprogressTracker.writecancel()
				print("Done")
			
			if SMLD.spotifyerror:
				showerror("Spotify API error", "Spotify API returned error code 400. Is Spotify API configured in the settings?")
				SMLD.spotifyerror = False

			if SMLD.spotifyerror2:
				showerror("Spotify API error", "Spotify API returned error code 404. Is the link valid?")
				cancel()
				SMLD.spotifyerror2 = False

			try:
				songinfo1.setText("Artist: "+ str(SMLD.artisttoshow))
				songinfo2.setText("Song: "+ str(SMLD.songnametoshow))
				if str(SMLD.albumnametoshow):
					songinfo3.setText("Album: "+ str(SMLD.albumnametoshow))

				pg.setText("Progress: "+ str(progresstoshow) + "%")
				np.setText(f"  Songs downloaded: {str(remainingtoshow)} / {str(totaltoshow)} ")

				rd.setText("Rate is: "+ str(rate) + " SPM")
			except Exception:
				pass

		def setupSMLD():
			pathtocheck = libraryDirInputBox.text()
			global done
			resetfiles()
			number = 0
			while number < 17:
				poistettava = os.path.join(getBaseConfigDir(),"SMLD", "Temp", "Songlist" + str(number) +".txt")
				if os.path.isfile(poistettava):
					os.remove(poistettava)
					print("Removed songlist: "+ str(number))
				number = number + 1

			if os.path.isfile(pathtocheck) or "open.spotify.com"in str(pathtocheck) or "youtube.com"in str(pathtocheck):
				downloadb1.setEnabled(False)
				fileformatDropdown.setEnabled(False)

				cancelb.setVisible(True)
				pg.setVisible(True)
				np.setVisible(True)
				rd.setVisible(True)

				SMLD.libraryfiledirectory = pathtocheck

				SMLD.cancel = False

				SMLD.fileformat = self.fileformat

				done = False

				self.refresherTimer.start(1)
				threadcount = int(Settings["SMLD-mutithreading"])
				SMLD.setupSMLD(threadcount, str(currentlibrarydirectory))
				songinfo2.setVisible(True)
				songinfo1.setVisible(True)
				songinfo3.setVisible(True)


			else:
				#qtw.QMessageBox.warning(self, "File not found", "File cannot be found or it doesn't exist. Please enter a valid file path.")
				showerror("File not found", "File cannot be found or it doesn't exist. Please enter a valid file path.")

		self.refresherTimer = qtc.QTimer(self, singleShot=True)
		self.refresherTimer.timeout.connect(refresher)

		frame1 = qtw.QFrame(self)
		self.layout.addWidget(frame1, 4, 1, 1, 4)	#kuudes parametry jätettynä tyhjäksi venyttää widgetin viemään koko solun tilan     viides parametri = monta saraketta grid vie
		frame1layout = qtw.QHBoxLayout(frame1)
		frame1layout.setContentsMargins(0,0,0,0)

		fileformatDropdown = qtw.QComboBox(frame1)
		fileformatDropdown.addItems(fileformats.keys())
		def fileformatChanged(to):
			self.fileformat = to
		fileformatDropdown.currentTextChanged.connect(fileformatChanged)
		frame1layout.addWidget(fileformatDropdown)

		def cancel():
			SMLD.cancel = True


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
