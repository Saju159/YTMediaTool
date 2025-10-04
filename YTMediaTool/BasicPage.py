import math, re
import PySide6.QtWidgets as qtw
import PySide6.QtGui as qtg
import PySide6.QtCore as qtc
from queue import Empty as QueueEmpty
from Common import openDirInFileBrowser, openFilePicker, createYDLProcess, cleanupYDLTemp
import Info
from Settings import Settings, setSetting
from SettingsPage import HelpBtn

class DownloadProgressDialog(qtw.QDialog):
	def __init__(self, window: qtw.QWidget):
		super().__init__(window)

		self.hasBeenCanceled = False

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

		self.rootlayout = qtw.QVBoxLayout(self)

		urlregex = re.compile(Info.urlregex)
		print("urlregex: "+Info.urlregex)

		def validate():
			ff = Info.fileformats[containerOptCombobox.currentText()]
			urlregexmatch = urlregex.fullmatch(urlInputBox.text().strip())
			# print(urlregexmatch and urlregexmatch.group(1,2,3,4) or None)

			if ("video" in ff and ff["video"] == True) and not dlVideoOptCheckbox.isChecked() and not dlAudioOptCheckbox.isChecked():
				self.statusLabel.setText("Neither video nor audio downloading is enabled!")
			elif urlInputBox.text().strip() == "":
				self.statusLabel.setText("")
			elif not (urlregexmatch != None and len(urlregexmatch.group(2)) > 0):
				self.statusLabel.setText("Invalid URL!")
			else:
				self.statusLabel.setVisible(False)
				downloadButton.setEnabled(True)
				return

			self.statusLabel.setVisible(True)
			downloadButton.setEnabled(False)

		# URL box
		urlInputBox = qtw.QLineEdit(self, placeholderText="URL to download from", clearButtonEnabled=True)
		urlInputBox.textChanged.connect(validate)
		self.rootlayout.addWidget(urlInputBox)

		self.optslayout = qtw.QFormLayout()
		self.rootlayout.addLayout(self.optslayout)

		def updateOpts():
			setSetting("BasicPage-Format", str(containerOptCombobox.currentText()))
			setSetting("BasicPage-DLVideo", bool(dlVideoOptCheckbox.isChecked()))
			setSetting("BasicPage-DLAudio", bool(dlAudioOptCheckbox.isChecked()))
			setSetting("BasicPage-VideoQuality", str(videoQualityOptCombobox.currentText()))
			setSetting("YDL-DLFilenameTemplate", str(fnameTmplOptCustomInputBox.text()))
			setSetting("BasicPage-DownloadDir", str(downloadDirInputBox.text()))
			validate()

		# Container format option
		containerOptFrame = qtw.QFrame(self)
		containerOptFrameLayout = qtw.QHBoxLayout(containerOptFrame)
		containerOptFrameLayout.setContentsMargins(0,0,0,0)
		self.optslayout.addRow("Container:", containerOptFrame)

		def containerOptChanged(val):
			ff = Info.fileformats[val]
			if "video" in ff and ff["video"] == True:
				dlVideoOptCheckbox.setVisible(True)
				dlAudioOptCheckbox.setVisible(True)
				audioOnlyLabel.setVisible(False)
				dlVideoOptChanged(Settings["BasicPage-DLVideo"])
			else:
				dlVideoOptCheckbox.setVisible(False)
				dlAudioOptCheckbox.setVisible(False)
				audioOnlyLabel.setVisible(True)
				dlVideoOptChanged(False)

			if "warn" in ff and window.isVisible(): # isVisible check so this warning is not shown during startup
				qtw.QMessageBox.warning(self, f"Warning on use of container format '{val}'", ff["warn"]) # FIXME make this into a button next to the format dropdown instead of a popup

			updateOpts()

		containerOptCombobox = qtw.QComboBox(containerOptFrame)
		containerOptCombobox.addItems(Info.fileformats.keys())
		containerOptCombobox.setCurrentText(Settings["BasicPage-Format"])
		containerOptCombobox.currentTextChanged.connect(containerOptChanged)

		# Include video option
		def dlVideoOptChanged(state):
			videoQualityOptLabel.setVisible(state)
			videoQualityOptCombobox.setVisible(state)

		dlVideoOptCheckbox = qtw.QCheckBox(containerOptFrame, text="Include &video", toolTip="If disabled, video download will be skipped.")
		dlVideoOptCheckbox.setChecked(Settings["BasicPage-DLVideo"])
		dlVideoOptCheckbox.stateChanged.connect(dlVideoOptChanged)
		dlVideoOptCheckbox.stateChanged.connect(updateOpts)

		# Include audio option
		dlAudioOptCheckbox = qtw.QCheckBox(containerOptFrame, text="Include &audio", toolTip="If disabled, audio download will be skipped.")
		dlAudioOptCheckbox.setChecked(Settings["BasicPage-DLAudio"])
		dlAudioOptCheckbox.stateChanged.connect(updateOpts)

		audioOnlyLabel = qtw.QLabel(containerOptFrame, text="This container only supports audio.", visible=False)

		containerOptFrameLayout.addWidget(containerOptCombobox)
		containerOptFrameLayout.addWidget(dlVideoOptCheckbox)
		containerOptFrameLayout.addWidget(dlAudioOptCheckbox)
		containerOptFrameLayout.addWidget(audioOnlyLabel)
		containerOptFrameLayout.addStretch(1)

		# Video quality option
		videoQualityOptLabel = qtw.QLabel(self, text="Video quality:")
		videoQualityOptCombobox = qtw.QComboBox(self)
		videoQualityOptCombobox.addItems(Info.videoqualities.keys())
		videoQualityOptCombobox.setCurrentText(Settings["BasicPage-VideoQuality"])
		videoQualityOptCombobox.currentTextChanged.connect(updateOpts)
		self.optslayout.addRow(videoQualityOptLabel, videoQualityOptCombobox)

		# Filename template option
		def fnameTmplOptComboboxChanged(val):
			if val == "Custom":
				fnameTmplOptCustomInputBox.setEnabled(True)
				fnameTmplOptCustomInputBox.setToolTip("Custom filename template")
			else:
				fnameTmplOptCustomInputBox.setText(Info.filenametemplates[val])
				fnameTmplOptCustomInputBox.setEnabled(False)
				fnameTmplOptCustomInputBox.setToolTip("Preview of the currently selected filename template")

		fnameTmplOptCombobox = qtw.QComboBox(self, toolTip="Filename template for downloaded files")
		fnameTmplOptCombobox.addItems(Info.filenametemplates.keys())
		fnameTmplOptCombobox.addItem(qtg.QIcon.fromTheme("edit-entry"), "Custom")
		fnameTmplOptCombobox.setCurrentText("Custom")
		fnameTmplOptCombobox.currentTextChanged.connect(fnameTmplOptComboboxChanged)
		self.optslayout.addRow("Filename:", fnameTmplOptCombobox)

		fnameTmplOptCustomFrame = qtw.QFrame(self)
		fnameTmplOptCustomFrameLayout = qtw.QHBoxLayout(fnameTmplOptCustomFrame)
		fnameTmplOptCustomFrameLayout.setContentsMargins(0,0,0,0)
		self.optslayout.addWidget(fnameTmplOptCustomFrame)

		fnameTmplOptCustomInputBox = qtw.QLineEdit(fnameTmplOptCustomFrame)
		fnameTmplOptCustomInputBox.setText(Settings["YDL-DLFilenameTemplate"])
		for key, val in Info.filenametemplates.items():
			if val == Settings["YDL-DLFilenameTemplate"]:
				fnameTmplOptCombobox.setCurrentText(key)
				break
		fnameTmplOptCustomInputBox.textChanged.connect(updateOpts)
		fnameTmplOptCustomFrameLayout.addWidget(fnameTmplOptCustomInputBox, 1)
		fnameTmplOptCustomFrameLayout.addWidget(HelpBtn(self, "https://github.com/yt-dlp/yt-dlp?tab=readme-ov-file#output-template"), 0, qtc.Qt.AlignmentFlag.AlignRight)

		# Download directory option
		downloadDirFrame = qtw.QFrame(self)
		downloadDirFrameLayout = qtw.QHBoxLayout(downloadDirFrame)
		downloadDirFrameLayout.setContentsMargins(0,0,0,0)
		self.optslayout.addRow("Save files to:", downloadDirFrame)

		downloadDirInputBox = qtw.QLineEdit(downloadDirFrame, toolTip="Directory to save downloaded files to")
		downloadDirInputBox.setText(Settings["BasicPage-DownloadDir"])
		downloadDirInputBox.textChanged.connect(updateOpts)

		def seldir():
			picked_dir = openFilePicker(window, "openDir", title="Select directory to save downloaded files to")
			if picked_dir:
				downloadDirInputBox.setText(picked_dir)

		selectDirButton = qtw.QToolButton(self, text="Browse...", icon=qtg.QIcon.fromTheme(qtg.QIcon.ThemeIcon.FolderOpen), toolTip="Browse...")
		selectDirButton.clicked.connect(seldir)

		downloadDirFrameLayout.addWidget(downloadDirInputBox, 1)
		downloadDirFrameLayout.addWidget(selectDirButton)

		# Bottom separator
		self.rootlayout.addWidget(qtw.QFrame(self, frameShape=qtw.QFrame.Shape.HLine))

		self.bottomlayout = qtw.QHBoxLayout()
		self.rootlayout.addLayout(self.bottomlayout)

		self.statusLabel = qtw.QLabel(self, text="", textInteractionFlags=qtc.Qt.TextInteractionFlag.TextSelectableByMouse)

		def downloadf():
			downloadButton.setEnabled(False)

			input2 = urlInputBox.text().strip()

			progressWindow = DownloadProgressDialog(window)
			progressWindow.setWindowTitle(input2)

			def endFunc(returnStr, r2):
				progressWindow.destroy()

				dText, success = None, False
				if returnStr == "invalidDownloadInput": dText = "Invalid URL!"
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
							openDirInFileBrowser(Settings["BasicPage-DownloadDir"])

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

			ff = Info.fileformats[Settings["BasicPage-Format"]]

			process, returnPipe, statusQueue = createYDLProcess(
				url=input2,
				path=Settings["BasicPage-DownloadDir"],
				fileformat=Settings["BasicPage-Format"],
				dlvideo=("video" in ff and ff["video"] == True) and Settings["BasicPage-DLVideo"] or False,
				dlaudio=("video" in ff and ff["video"] == True) and Settings["BasicPage-DLAudio"] or True,
				videoquality=Settings["BasicPage-VideoQuality"]
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

		downloadButton = qtw.QPushButton(self, text="&Download", icon=qtg.QIcon.fromTheme("download"))
		downloadButton.clicked.connect(downloadf)

		self.bottomlayout.addWidget(self.statusLabel, 1)
		self.bottomlayout.addWidget(downloadButton, 0, qtc.Qt.AlignmentFlag.AlignRight)

		# Update initial state
		dlVideoOptChanged(dlVideoOptCheckbox.isChecked())
		containerOptChanged(containerOptCombobox.currentText())




