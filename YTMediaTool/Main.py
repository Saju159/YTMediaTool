from sys import argv, exit

if len(argv) > 1 and argv[1] == "--version":
	import Version
	print(f"{Version.Name} {Version.Version} - {Version.ShortDesc}\n{Version.GPLNotice}")
	exit()

if __name__ == "__main__": # Only run if this is the main process.
	import os
	import PySide6.QtWidgets as qtw
	from Common import getBaseConfigDir
	import Settings

	if not os.path.exists(os.path.join(getBaseConfigDir(),"SMLD")):
		os.makedirs(os.path.join(getBaseConfigDir(),"SMLD"))

	if not os.path.exists(os.path.join(getBaseConfigDir(),"SMLD", "Temp")):
		os.makedirs(os.path.join(getBaseConfigDir(),"SMLD", "Temp"))

	with open(os.path.join(getBaseConfigDir(),"SMLD", "Temp", "progress.txt"), "w") as f:
		f.close()

	with open(os.path.join(getBaseConfigDir(),"SMLD", "Temp", "cancel.txt"), "w") as f:
		f.write("0")
		f.close()

	class MainWindow(qtw.QMainWindow):
		def __init__(self):
			super().__init__()

			tabFrame = qtw.QTabWidget(self)
			self.setCentralWidget(tabFrame)

			pageNames = {
				"BasicPage": "Basic",
				# "SMLDpage": "SMLD",
				"SettingsPage": "Settings",
				"AboutPage": "About"
			}
			pages = []

			i = 0
			for pageName in pageNames.keys():
				pageModule = __import__(pageName)
				page = pageModule.Page(self)
				tabFrame.addTab(page, pageNames[pageName])

				pages.insert(i, page)

				i += 1



	application = qtw.QApplication(argv)
	window = MainWindow()
	window.setWindowTitle("YTMediaTool")
	# window.geometry('600x480')
	# window.minsize(600, 34)
	# window.resizable(width=False, height=False)
	window.show()

	if not os.path.isfile(Settings.Settings["FFmpeg_path"]):
		print(f'FFmpeg cannot be found in: "{Settings.Settings["FFmpeg_path"]}". Please enter a valid FFmpeg path in the settings.')

	def quit(code):
		with open(os.path.join(getBaseConfigDir(),"SMLD", "Temp", "cancel.txt"), "w") as f:
			f.write("1")
			f.close()
		Settings.saveSettingsToFile()
		exit(code)

	quit(application.exec())
