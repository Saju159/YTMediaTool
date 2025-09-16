import PySide6.QtWidgets as qtw
import PySide6.QtCore as qtc
import PySide6.QtGui as qtg
import Version

class Page(qtw.QScrollArea):
	def __init__(self, window: qtw.QWidget):
		super().__init__(window)

		widget = qtw.QWidget(self)
		self.setWidget(widget)
		self.setWidgetResizable(True)

		self.layout = qtw.QVBoxLayout(widget)
		self.layout.setSizeConstraint(qtw.QLayout.SizeConstraint.SetMinimumSize)

		self.label = qtw.QLabel(widget, text=
			f"""# {Version.Name} {Version.Version}
			\n{Version.ShortDesc}
			\n{Version.GPLNotice}""",
			textFormat=qtc.Qt.TextFormat.MarkdownText,
			wordWrap=True,
			textInteractionFlags= qtc.Qt.TextInteractionFlag.TextSelectableByMouse | qtc.Qt.TextInteractionFlag.TextBrowserInteraction,
			openExternalLinks=True)
		self.layout.addWidget(self.label)

		self.sourceCodeBtn = qtw.QPushButton(widget, text="&Source code:\nhttps://github.com/Saju159/YTMediaTool")
		self.sourceCodeBtn.clicked.connect(lambda: qtg.QDesktopServices.openUrl("https://github.com/Saju159/YTMediaTool"))
		self.layout.addWidget(self.sourceCodeBtn)
