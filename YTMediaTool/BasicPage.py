import math
import PySide6.QtWidgets as qtw
import PySide6.QtGui as qtg
import PySide6.QtCore as qtc
from queue import Empty as QueueEmpty
from Common import openDirInFileBrowser, openFilePicker, createYDLProcess, cleanupYDLTemp
import Info
from Settings import Settings

class DownloadProgressDialog(qtw.QDialog):
	def __init__(self, window: qtw.QWidget):
		super().__init__(window)

		self.hasBeenCanceled = False

		self.setWindowTitle(" ")

		self.layout = qtw.QVBoxLayout(self)
		self.layout.setSizeConstraint(qtw.QLayout.SizeConstraint.SetFixedSize)

		self.pLabel = qtw.QLabel(self, text="Preparing download...")
		self.layout.addWidget(self.pLabel)

		self.pDownloadedLabel = qtw.QLabel(self)
		self.layout.addWidget(self.pDownloadedLabel)

		self.pProgressBar = qtw.QProgressBar(self, minimum=0, maximum=0)
		self.pProgressBar.setMinimumWidth(360)
		self.layout.addWidget(self.pProgressBar)

		self.pButtonBox = qtw.QDialogButtonBox(self, standardButtons=qtw.QDialogButtonBox.StandardButton.Cancel)
		self.pButtonBox.rejected.connect(self.reject)
		self.layout.addWidget(self.pButtonBox)

	def reject(self):
		if not self.hasBeenCanceled:
			self.hasBeenCanceled = True
			self.pLabel.setText("Cancelling...")
			self.rejected.emit()

class Page(qtw.QWidget):
	def __init__(self, window: qtw.QWidget):
		super().__init__()

		layout = qtw.QFormLayout(self)

		# Mode
		modes = [
			"Download from URL",
			"Search & Download from YouTube",
		]
		self.mode = modes[0]
		self.modenum = 0

		def selection(val):
			self.mode = val
			self.modenum = modes.index(self.mode)
			if self.modenum == 0:
				urlLabel.setText("URL: ")
			elif self.modenum == 1:
				urlLabel.setText("Search term: ")

		modeLabel = qtw.QLabel(self, text="Mode: ")
		modeDropdown = qtw.QComboBox(self)
		modeDropdown.addItems(modes)
		modeDropdown.currentTextChanged.connect(selection)
		layout.addRow(modeLabel, modeDropdown)

		# URL box
		urlLabel = qtw.QLabel(self, text="URL: ")
		urlInputBox = qtw.QLineEdit(self)
		layout.addRow(urlLabel, urlInputBox)

		# File format
		ffLabel = qtw.QLabel(self, text="Format: ")
		ffFrame = qtw.QFrame(self)
		ffFrameLayout = qtw.QHBoxLayout(ffFrame)
		ffFrameLayout.setContentsMargins(0,0,0,0)
		layout.addRow(ffLabel, ffFrame)

		self.dlvideo = bool(Settings["BasicPage-DLVideo"])
		self.dlaudio = bool(Settings["BasicPage-DLAudio"])
		self.fileformat = str(Settings["BasicPage-Format"])
		self.vq = str(Settings["BasicPage-VideoQuality"])
		self.dirSV = str(Settings["BasicPage-DownloadDir"])
  #
		def onSaveableSettingUpdate():
			self.dlvideo = dlvideoCheckbox.isChecked()
			Settings["BasicPage-DLVideo"] = bool(self.dlvideo)

			self.dlaudio = dlaudioCheckbox.isChecked()
			Settings["BasicPage-DLAudio"] = bool(self.dlaudio)

			self.fileformat = fileformatDropdown.currentText()
			Settings["BasicPage-Format"] = str(self.fileformat)

			self.vq = vqDropdown.currentText()
			Settings["BasicPage-VideoQuality"] = str(self.vq)

			self.dirSV = dirInputBox.text()
			Settings["BasicPage-DownloadDir"] = str(self.dirSV)

		def ffselection(val):
			ff = Info.fileformats[val]
			if "video" in ff and ff["video"] == True:
				dlvideoCheckbox.setEnabled(True)
				dlvideoselection(self.dlvideo)
			else:
				dlvideoCheckbox.setEnabled(False)
				dlvideoselection(False)

			if "warn" in ff and window.isVisible(): # isVisible check so this warning is not shown during startup
				msgbox = qtw.QMessageBox(self, windowTitle="Warning", text=ff["warn"]) # FIXME make this into a button next to the format dropdown instead of a popup
				msgbox.show()

			onSaveableSettingUpdate()

		fileformatDropdown = qtw.QComboBox(ffFrame) #fileformat, next(iter(Info.fileformats)), *Info.fileformats, command=lambda _: ffselection())
		fileformatDropdown.addItems(Info.fileformats.keys())
		fileformatDropdown.setCurrentText(self.fileformat)
		fileformatDropdown.currentTextChanged.connect(ffselection)

		def dlvideoselection(state):
			vqLabel.setHidden(not state)
			vqDropdown.setHidden(not state)
			onSaveableSettingUpdate()

		dlvideoCheckbox = qtw.QCheckBox(ffFrame, text="&Video", checked=self.dlvideo, toolTip="Should the video be downloaded?")
		dlvideoCheckbox.stateChanged.connect(dlvideoselection)

		dlaudioCheckbox = qtw.QCheckBox(ffFrame, text="&Audio", checked=self.dlaudio, toolTip="Should the audio be downloaded?")
		dlaudioCheckbox.stateChanged.connect(onSaveableSettingUpdate)

		ffFrameLayout.addWidget(fileformatDropdown)
		ffFrameLayout.addWidget(dlvideoCheckbox)
		ffFrameLayout.addWidget(dlaudioCheckbox)

		# Video quality
		vqLabel = qtw.QLabel(self, text="Video quality: ")
		vqDropdown = qtw.QComboBox(self)
		vqDropdown.addItems(Info.videoqualities.keys())
		vqDropdown.setCurrentText(self.vq)
		vqDropdown.currentTextChanged.connect(onSaveableSettingUpdate)
		layout.addRow(vqLabel, vqDropdown)

		# Destination Directory
		dirLabel = qtw.QLabel(self, text="Destination directory: ")
		dirFrame = qtw.QFrame(self)
		dirFrameLayout = qtw.QHBoxLayout(dirFrame)
		dirFrameLayout.setContentsMargins(0,0,0,0)
		layout.addRow(dirLabel, dirFrame)

		dirInputBox = qtw.QLineEdit(dirFrame)
		dirInputBox.setText(self.dirSV)
		dirInputBox.textChanged.connect(onSaveableSettingUpdate)

		def seldir():
			picked_dir = openFilePicker(window, "openDir", title="Select directory to save downloaded files to...")
			if picked_dir:
				dirInputBox.setText(picked_dir)

		selectDirButton = qtw.QToolButton(self, text="Browse...", icon=qtg.QIcon.fromTheme(qtg.QIcon.ThemeIcon.FolderOpen), toolTip="Browse...")
		selectDirButton.clicked.connect(seldir)

		dirFrameLayout.addWidget(dirInputBox)
		dirFrameLayout.addWidget(selectDirButton)

		bottomVSpacer = qtw.QSpacerItem(0, 0, qtw.QSizePolicy.Policy.Expanding, qtw.QSizePolicy.Policy.Expanding)
		layout.addItem(bottomVSpacer)

		statusBarSeparator = qtw.QFrame(self, frameShape=qtw.QFrame.Shape.HLine)
		layout.addRow(statusBarSeparator)

		def downloadf():
			downloadButton.setEnabled(False)

			input2 = urlInputBox.text().strip()

			progressWindow = DownloadProgressDialog(window)

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
					qtw.QMessageBox.warning(self, "Download error", dText)
				elif success:
					print("Download success!")
					if Settings["BasicPage-ShowDialogAfterDLSuccess"] == True:
						answer = qtw.QMessageBox.question(self, "Download finished", "Download finished.\nOpen destination directory?")
						if answer == qtw.QMessageBox.StandardButton.Yes:
							openDirInFileBrowser(self.dirSV)

			def checkStatus():
				if canceled:
					endFunc("canceled", None)
					downloadButton.setEnabled(True)
				dataAvailable = returnPipe.poll(0)
				if dataAvailable:
					try:
						rTuple = returnPipe.recv()
						if type(rTuple) == str:
							returnStr, errorStr = rTuple, None
						elif type(rTuple) == tuple:
							returnStr, errorStr = rTuple[0], rTuple[1]
						endFunc(returnStr, errorStr)
						downloadButton.setEnabled(True)
					except EOFError:
						# return pipe broken prematurely (most likely just canceled)
						downloadButton.setEnabled(True)
				else:
					try:
						dlStatus = statusQueue.get(False)
						progressWindow.pLabel.setText(dlStatus["progressWindowLabel"])
						if dlStatus["phase"] == "download":
							downloaded_bytes = float(dlStatus["downloaded_bytes"])
							progressWindow.pDownloadedLabel.setText("Downloaded:")

							if "total_bytes" in dlStatus:
								total_bytes = float(dlStatus["total_bytes"])
								downloadPercent = downloaded_bytes/total_bytes

								progressWindow.pDownloadedLabel.setText(f"{round(downloaded_bytes/1000000, 2)}MB/{round(total_bytes/1000000, 2)}MB {("total_bytes_is_estimate" in dlStatus and "(estimate) " or "")}downloaded {("speed" in dlStatus and f"at {round(dlStatus["speed"]/1000000, 2)}MB/s" or "")}")
								progressWindow.pProgressBar.setMaximum(100)
								progressWindow.pProgressBar.setValue(math.floor(downloadPercent*100))
							else:
								progressWindow.pDownloadedLabel.setText(f"{round(downloaded_bytes/1000000, 2)}MB downloaded")
								progressWindow.pProgressBar.setMaximum(0)

						else:
							progressWindow.pDownloadedLabel.setText("")
							progressWindow.pProgressBar.setMaximum(0)

					except QueueEmpty:
						pass
					timer.start(100)

			process, returnPipe, statusQueue = createYDLProcess(
				url=(self.modenum == 1 and "ytsearch:"+input2 or input2),
				path=self.dirSV,
				fileformat=self.fileformat,
				dlvideo=self.dlvideo,
				dlaudio=self.dlaudio,
				videoquality=self.vq
			)
			process.start()

			timer = qtc.QTimer(progressWindow, singleShot=True)
			timer.timeout.connect(checkStatus)
			timer.start(100)

			canceled = False
			def cancelf():
				progressWindow.pButtonBox.setEnabled(False)
				nonlocal canceled
				canceled = True
				process.terminate()
				delay = qtc.QTimer(self, singleShot=True)
				delay.timeout.connect(cleanupYDLTemp)
				delay.start(200)

			progressWindow.rejected.connect(cancelf)

			def skip(): pass
			progressWindow.setModal(True)

			progressWindow.show()
			progressWindow.exec()

		downloadButton = qtw.QPushButton(self, text="&Download")
		downloadButton.clicked.connect(downloadf)
		layout.addWidget(downloadButton)

		dlvideoselection(self.dlvideo)
		ffselection(self.fileformat)
		selection(modes[0])





