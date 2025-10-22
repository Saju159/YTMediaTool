import PySide6.QtWidgets as qtw

class ProgressDialog(qtw.QDialog):
	def __init__(self, parentWidget: qtw.QWidget=None, windowTitle: str=None, initialTask="Preparing..."):
		super().__init__(parentWidget, windowTitle=windowTitle)

		self.hasBeenCanceled = False
		self.current = 0
		self.target = 0
		self.isDownload = False
		self.rate = 0

		self.layout = qtw.QVBoxLayout(self)
		self.layout.setSizeConstraint(qtw.QLayout.SizeConstraint.SetFixedSize)

		self.pTaskLabel = qtw.QLabel(self, text=initialTask)
		self.layout.addWidget(self.pTaskLabel)

		self.pDownloadedLabel = qtw.QLabel(self)
		self.layout.addWidget(self.pDownloadedLabel)

		self.pProgressBar = qtw.QProgressBar(self, minimum=0, maximum=0)
		self.pProgressBar.setMinimumWidth(360)
		self.layout.addWidget(self.pProgressBar)

		self.pButtonBox = qtw.QDialogButtonBox(self, standardButtons=qtw.QDialogButtonBox.StandardButton.Cancel)
		self.pButtonBox.rejected.connect(self.reject)
		self.layout.addWidget(self.pButtonBox)

	def reset(self):
		self.current = 0
		self.target = 0
		self.isDownload = False
		self.rate = 0

		self.pTaskLabel.setText("")
		self.pDownloadedLabel.setText("")
		self.pProgressBar.setMaximum(0)

	def updateTask(self, task: str=""):
		self.pTaskLabel.setText(task)

	def updateProgress(self, current: int|float|None=None, target: int|float|None=None, targetIsEstimate=False, rate: int|float|None=None, isDownload=False):
		self.current = current or self.current
		self.target = target or self.target
		self.isDownload = isDownload
		self.rate = rate or self.rate

		if self.isDownload:
			self.pDownloadedLabel.setText(f"{round(self.current/1000000, 2)} MB out of {round(self.target/1000000, 2) if self.target > 0 else "???"} MB {"(estimate) " if targetIsEstimate else ""}downloaded {f"at {round(rate/1000000, 2)}MB/s" if self.rate > 0 else ""}")
		else:
			self.pDownloadedLabel.setText("")
		self.pProgressBar.setMaximum(self.target)
		self.pProgressBar.setValue(self.current)

	def reject(self):
		if not self.hasBeenCanceled:
			self.hasBeenCanceled = True
			self.reset()
			self.pTaskLabel.setText("Cancelling...")
			self.rejected.emit()
