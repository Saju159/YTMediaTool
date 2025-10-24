from sys import argv, exit

if len(argv) > 1 and argv[1] == "--version":
	import Version
	print(f"{Version.Name} {Version.Version} - {Version.ShortDesc}\n{Version.GPLNotice}")
	exit()

if __name__ == "__main__": # Only run if this is the main process.
	import os
	import sys
	import PySide6.QtWidgets as qtw
	from Common import getBaseConfigDir
	import YtdlpManager
	import Settings

	sys.path.insert(0, str(YtdlpManager.YtdlpPath))

	class MainWindow(qtw.QMainWindow):
		def __init__(self):
			super().__init__()

			tabFrame = qtw.QTabWidget(self)
			self.setCentralWidget(tabFrame)

			pageNames = {
				"BasicPage": "Basic",
				"SMLDpage": "SMLD",
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

	try:
		ytdlpModule = __import__("yt_dlp")
		YtdlpManager.UpdateYtdlpPackageInfo(ytdlpModule.version.__version__, os.path.dirname(ytdlpModule.__file__))

		window = MainWindow()
		window.setWindowTitle("YTMediaTool")
		window.show()

		if not os.path.isfile(Settings.Settings["FFmpeg_path"]):
			print(f'FFmpeg cannot be found in: "{Settings.Settings["FFmpeg_path"]}". Please enter a valid FFmpeg path in the settings.')
		code = application.exec()
		with open(os.path.join(getBaseConfigDir(),"SMLD", "Temp", "cancel.txt"), "w") as f:
			f.write("1")
			f.close()
		Settings.saveSettingsToFile()
		exit(code)

	except ModuleNotFoundError:
		answer = qtw.QMessageBox.question(None, "YTMediaTool", "YTMediaTool requires yt-dlp for downloading media, but it isn't installed on your system.\n\nWould you like for YTMediaTool to locally manage it and download it now?\n(clicking no quits the application)")
		if answer == qtw.QMessageBox.StandardButton.Yes:
			def updateFinish(r):
				if r == True:
					qtw.QMessageBox.information(None, "YTMediaTool", "yt-dlp was successfully downloaded! Please relaunch the application.")
					Settings.saveSettingsToFile() # last yt-dlp update time is saved to settings so write those to disk
					exit(0)
				else:
					exit(1)
			YtdlpManager.UpdateYtdlp(None, False, updateFinish)
			exit(application.exec())
		else:
			# User rejected locally managed
			exit(0)

	except ImportError as err:
		qtw.QMessageBox.critical(None, "Error", f"Error while loading yt-dlp module!\n{err}\n\nPlease report this at https://github.com/Saju159/YTMediaTool/issues")
		exit(1)
