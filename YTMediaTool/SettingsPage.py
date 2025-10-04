import os
import PySide6.QtWidgets as qtw
import PySide6.QtGui as qtg
import PySide6.QtCore as qtc
from Common import openFilePicker, getBaseConfigDir
from sys import platform

import Settings

class HelpBtn(qtw.QToolButton):
	def __init__(self, parent: qtw.QWidget, helptext: str):
		super().__init__(parent)

		self.setText("?")
		self.setIcon(qtg.QIcon.fromTheme(qtg.QIcon.ThemeIcon.HelpFaq))
		self.setToolTip(helptext)
		self.setFixedSize(22,22)
		if helptext[:8] == "https://":
			self.setToolTip("Click to open in browser:\n"+helptext)
			self.clicked.connect(lambda: qtg.QDesktopServices.openUrl(helptext))
		else:
			def showTip():
				qtw.QToolTip.showText(qtg.QCursor.pos(), helptext)
			self.clicked.connect(showTip)

class BaseOptFrame(qtw.QFrame):
	def __init__(self, parent: qtw.QWidget):
		super().__init__(parent)

		self.val = None

		self.layout = qtw.QHBoxLayout(self)
		self.layout.setContentsMargins(0,0,0,0)

class TextInputOption(BaseOptFrame):
	def reset(self):
		self.inputBox.setText(str(Settings.Settings[self.optId]))

	def modified(self, newVal):
		if newVal == None:
			newVal = ""
		self.val = newVal
		if self.val != Settings.Settings[self.optId]:
			self.page.showButtonsFrame()

	def __init__(self, parent: qtw.QWidget, page, optId: str, text: str, helptext: str|None=None, isfilepath: bool|None=False):
		super().__init__(parent)

		self.page = page
		self.page.opts[optId] = self
		self.optId = optId

		label = qtw.QLabel(self, text=f"{text}: ")
		self.layout.addWidget(label)
		self.inputBox = qtw.QLineEdit(self)
		self.inputBox.textChanged.connect(self.modified)
		self.reset()
		self.layout.addWidget(self.inputBox)

		if isfilepath:
			def seldir():
				picked_dir = openFilePicker(parent, "openFile")
				if picked_dir:
					self.inputBox.setText(picked_dir)

			selectDirButton = qtw.QToolButton(self, text="Browse...", icon=qtg.QIcon.fromTheme(qtg.QIcon.ThemeIcon.DocumentOpen), toolTip="Browse...")
			selectDirButton.clicked.connect(seldir)
			self.layout.addWidget(selectDirButton)

		if type(helptext) == str:
			helpBtn = HelpBtn(self, helptext)
			self.layout.addWidget(helpBtn)

class BooleanOption(BaseOptFrame):
	def reset(self):
		self.val = Settings.Settings[self.optId]
		self.checkBox.setChecked(self.val)

	def modified(self, newVal):
		self.val = self.checkBox.isChecked()
		if self.val != Settings.Settings[self.optId]:
			self.page.showButtonsFrame()

	def __init__(self, parent: qtw.QWidget, page, optId: str, text: str, helptext: None=str|None):
		super().__init__(parent)

		self.page = page
		self.page.opts[optId] = self
		self.optId = optId

		self.checkBox = qtw.QCheckBox(self, text=text)
		self.checkBox.stateChanged.connect(self.modified)
		self.reset()
		self.layout.addWidget(self.checkBox, 0)

		if type(helptext) == str:
			helpBtn = HelpBtn(self, helptext)
			self.layout.addWidget(helpBtn)

		self.layout.addStretch()

class DropdownOption(BaseOptFrame):
	def reset(self):
		self.val = Settings.Settings[self.optId]
		self.dropdown.setCurrentText(self.val)

	def modified(self, newVal):
		self.val = newVal
		if self.val != Settings.Settings[self.optId]:
			self.page.showButtonsFrame()

	def __init__(self, parent: qtw.QWidget, page, optId: str, text: str, choices: list, helptext: None=str|None):
		super().__init__(parent)

		self.page = page
		self.page.opts[optId] = self
		self.optId = optId

		label = qtw.QLabel(self, text=f"{text}: ")
		self.layout.addWidget(label, 0)
		self.dropdown = qtw.QComboBox(self)
		self.dropdown.addItems(choices)
		self.dropdown.currentTextChanged.connect(self.modified)
		self.reset()
		self.layout.addWidget(self.dropdown)

		if type(helptext) == str:
			helpBtn = HelpBtn(self, helptext)
			self.layout.addWidget(helpBtn)

		self.layout.addStretch()

class SpinBoxOption(BaseOptFrame):
	def reset(self):
		self.spinbox.setValue(Settings.Settings[self.optId])

	def modified(self, newVal):
		self.val = newVal
		if self.val != Settings.Settings[self.optId]:
			self.page.showButtonsFrame()

	def __init__(self, parent: qtw.QWidget, page, optId: str, text: str, minimum: 1=int, maximum: 100=int, helptext: None=str|None):
		super().__init__(parent)

		self.page = page
		self.page.opts[optId] = self
		self.optId = optId

		label = qtw.QLabel(self, text=f"{text}: ")
		self.layout.addWidget(label, 0)
		self.spinbox = qtw.QSpinBox(self, minimum=minimum, maximum=maximum)
		self.spinbox.valueChanged.connect(self.modified)
		self.reset()
		self.layout.addWidget(self.spinbox)

		if type(helptext) == str:
			helpBtn = HelpBtn(self, helptext)
			self.layout.addWidget(helpBtn)

		self.layout.addStretch()

class Spacer(qtw.QFrame):
	def __init__(self, parent: qtw.QWidget):
		super().__init__(parent)

		self.setFrameShape(qtw.QFrame.Shape.HLine)

class Button(qtw.QFrame):
	def __init__(self, parent: qtw.QWidget, page, text: str, pressfunc: callable):
		super().__init__(parent)

		self.layout = qtw.QHBoxLayout(self)
		self.layout.setContentsMargins(0,0,0,0)
		self.btn = qtw.QPushButton(self, text=text)
		self.btn.pressed.connect(pressfunc)
		self.layout.addWidget(self.btn)
		self.layout.addStretch()

class Page(qtw.QWidget):
	def loadSettings(self):
		for opt in self.opts.values():
			opt.reset()
		self.applyBtn.setEnabled(False)
		self.undoBtn.setEnabled(False)

	def showButtonsFrame(self):
		self.applyBtn.setEnabled(True)
		self.undoBtn.setEnabled(True)

	def __init__(self, window: qtw.QWidget):
		super().__init__(window)

		playout = qtw.QVBoxLayout(self)
		# playout.setContentsMargins(0,0,0,0)

		scrollarea = qtw.QScrollArea(self)
		playout.addWidget(scrollarea)
		widget = qtw.QWidget(scrollarea)
		scrollarea.setWidget(widget)
		scrollarea.setWidgetResizable(True)

		self.layout = qtw.QVBoxLayout(widget)

		self.opts = {}

		def applySettings():
			for key in self.opts:
				if key in Settings.Settings:
					Settings.setSetting(key, self.opts[key].val)
			Settings.saveSettingsToFile()
			self.applyBtn.setEnabled(False)
			self.undoBtn.setEnabled(False)

		self.layout.addWidget(TextInputOption(widget, self, "FFmpeg_path", "Path to FFmpeg executable", None, True))
		self.layout.addWidget(qtw.QLabel(widget, text="FFmpeg is required for merging the downloaded video + audio and for converting formats."))
		if platform == "win32":
			self.layout.addWidget(Button(widget, self, "Download FFmpeg for Windows from github.com/BtbN/FFmpeg-Builds", lambda: qtg.QDesktopServices.openUrl("https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip")))
		self.layout.addWidget(Button(widget, self, "Get binaries from https://www.ffmpeg.org/download.html", lambda: qtg.QDesktopServices.openUrl("https://www.ffmpeg.org/download.html")))

		self.layout.addWidget(Spacer(widget))
		self.layout.addWidget(qtw.QLabel(widget, text="Settings for 'Basic' tab:"))
		self.layout.addWidget(BooleanOption(widget, self, "YDL-EnablePlaylistDL", "Download playlist if URL leads to both a video and a playlist"))
		self.layout.addWidget(BooleanOption(widget, self, "YDL-SkipIfExists", "Skip download if already downloaded", "Will still show \"Download completed\" even if the file was already downloaded."))
		self.layout.addWidget(BooleanOption(widget, self, "BasicPage-ShowDialogAfterDLSuccess", "Show dialog after successful download"))
		self.layout.addWidget(DropdownOption(widget, self, "BasicPage-ForceQuality", "When video quality is not available", ["Resize to selected quality", "Download closest to selected quality"], "If \"Resize to selected quality\" is selected:\nCalls FFmpeg to resize the video after download if resolution doesn't match. This can be quite slow depending on the video's length and quality selected."))
		self.layout.addWidget(Spacer(widget))
		self.layout.addWidget(TextInputOption(widget, self, "YDL-CookiesFilePath", "Path to cookies.txt", "Path to a Netscape formatted cookies file.\nLeave blank to not use a cookie file.\n\nCookies should only be used if you keep getting blocked by YouTube or are downloading private videos.\n\nDisables \"Grab browser cookies\".", True))
		self.layout.addWidget(BooleanOption(widget, self, "BasicPage-Cookies", "Grab browser cookies", "Allows yt-dlp to grab your browser's cookies for authentication.\n\nIgnored if path to cookies.txt is not blank."))
		self.layout.addWidget(DropdownOption(widget, self, "BasicPage-browser", "Browser to grab cookies from", ["brave", "chrome", "chromium", "edge", "firefox", "opera", "safari", "vivaldi", "whale"], "This list is populated with browsers that yt-dlp supports grabbing cookies from."))

		self.layout.addWidget(Spacer(widget))
		self.layout.addWidget(qtw.QLabel(widget, text="Settings for 'SMLD' tab:"))
		self.layout.addWidget(Button(widget, self, "Open SMLD logs", lambda: qtg.QDesktopServices.openUrl(qtc.QUrl.fromLocalFile(os.path.join(getBaseConfigDir(),"SMLD","SMLDlog.txt")))))
		self.layout.addWidget(SpinBoxOption(widget, self, "SMLD-mutithreading", "Number of concurrent downloads (EXPERIMENTAL)", 2, 16))
		self.layout.addWidget(DropdownOption(widget, self, "SMLD-source", "Select the media download source", ["YouTube Music", "YouTube"]))
		self.layout.addWidget(BooleanOption(widget, self, "SMLD-useytmetadata", "Get metadata from YouTube Music."))

		self.layout.addStretch()

		self.buttonBar = qtw.QDialogButtonBox(self)
		self.applyBtn = self.buttonBar.addButton("&Apply && Save changes", qtw.QDialogButtonBox.ButtonRole.ApplyRole)
		self.applyBtn.clicked.connect(applySettings)
		self.undoBtn = self.buttonBar.addButton("&Undo", qtw.QDialogButtonBox.ButtonRole.RejectRole)
		self.undoBtn.clicked.connect(self.loadSettings)
		playout.addWidget(self.buttonBar)

		self.loadSettings()
