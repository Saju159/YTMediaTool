import json
import multiprocessing
import os
import pathlib
import sys
import time
import PySide6.QtCore as qtc
import PySide6.QtWidgets as qtw

from Common import DownloadError, downloadFile, getBaseConfigDir, isVersionNewer
from CommonGui import ProgressDialog
from Settings import setSetting

YtdlpReleasesApiUrl = "https://api.github.com/repos/yt-dlp/yt-dlp/releases/latest"
YtdlpApiDLPath = pathlib.Path(getBaseConfigDir(), "yt-dlp_latest.json") # File path to where API data will be downloaded to
YtdlpPath = pathlib.Path(getBaseConfigDir(), "lib", "yt-dlp") # File path to yt-dlp package
YtdlpVersion = None
YtdlpImportPath = None

def _UpdateTarget(
	inputPipe,
	outputPipe,
	confirmDownload: bool,
	apiDownloadOptional: bool,
	currentVer: str = None
):
	def pushStatus(task, current=0, target=0):
		outputPipe.send(("status", {"task": task, "current": current, "target": target}))

	def pushError(reason):
		outputPipe.send(("error", str(reason)))
		if isinstance(reason, Exception):
			raise reason
		else:
			raise Exception("No url or hash found in release data!")

	def pushCancel(reason):
		sys.exit(1)

	try:
		def decodeApi():
			with YtdlpApiDLPath.open("r") as f:
				return json.loads(f.read())

		def fetchApi(optional=False):
			if optional and YtdlpApiDLPath.is_file():
				try:
					return decodeApi()
				except json.JSONDecodeError:
					# existing api file decode failed, so re-download
					YtdlpApiDLPath.unlink()
					fetchApi(False)
			else:
				try:
					def statusCallback(task, current, target):
						if task == "downloading":
							pushStatus("Downloading release data...", current, target)
					downloadFile(url=YtdlpReleasesApiUrl, path=YtdlpApiDLPath, maxlength=2000000, statusCallback=statusCallback)
					return decodeApi()
				except DownloadError as err:
					pushError(f"Failed to download release data: {err.reason}")
				except json.JSONDecodeError as err:
					pushError(f"Failed to decode release data: {err.reason}")

		# Fetch releases from API
		pushStatus("Fetching release data...")
		data = fetchApi(apiDownloadOptional)

		# Parse release data
		pushStatus("Parsing release data...")
		try:
			tag = data["tag_name"]
			for asset in data["assets"]:
				if asset["name"] == "yt-dlp":
					url = asset["browser_download_url"]
					sha256 = asset["digest"][7:]
					break
		except Exception as err:
			pushError(err)

		if url == None:
			pushError("No url found in release data!")

		# Confirm download
		pushStatus("Awaiting...")

		if currentVer and not isVersionNewer(tag, currentVer):
			sys.exit(3)

		if confirmDownload:
			outputPipe.send(("confirmDownload", F"Download yt-dlp version {tag}?\n\nURL: {url}"))
			inputPipe.poll()
			answer = inputPipe.recv()
			if answer != True:
				# user did not accept downloading release
				return

		# Download release
		pushStatus("Downloading yt-dlp...")

		try:
			def statusCallback(task, current, target):
				if task == "downloading":
					pushStatus("Downloading yt-dlp...", current, target)
				elif task == "verifying":
					pushStatus("Verifying...", current, target)
				elif task == "moving":
					pushStatus("Finishing up...", current, target)
			downloadFile(url=url, path=YtdlpPath, sha256=sha256, statusCallback=statusCallback)
		except DownloadError as err:
			pushError(f"Failed to download yt-dlp: {err.reason}")

		pushStatus("Finishing up...")

		sys.exit(0)

	except EOFError:
		# pipe most likely dead on purpose, ignore
		sys.exit(1)
	except Exception as err:
		print(f"Unhandled exception during yt-dlp update: {err}")
		sys.exit(2)


def UpdateYtdlp(
	parentWidget: qtw.QWidget|None,
	confirmDownload: bool,
	finishCallback: callable
):
	now = int(time.time())
	setSetting("YDLManager-LastChecked", now)

	progDialog = ProgressDialog(parentWidget, windowTitle="Updating yt-dlp...")
	progDialog.setModal(True)
	progDialog.show()

	def finished(r):
		progDialog.destroy()
		finishCallback(r)

	apiDownloadOptional = False
	if YtdlpPath.is_file():
		mtime = int(os.path.getmtime(YtdlpPath))
		print("mtime: "+str(mtime))
		print("  now: "+str(now))
		if mtime+120 > now:
			apiDownloadOptional = True

	print("apiDownloadOptional = "+str(apiDownloadOptional))

	inputPipeRecv, inputPipeSend = multiprocessing.Pipe(duplex=False)
	outputPipeRecv, outputPipeSend = multiprocessing.Pipe(duplex=False)
	process = multiprocessing.Process(target=_UpdateTarget, args=(inputPipeRecv, outputPipeSend, confirmDownload, apiDownloadOptional, YtdlpVersion))

	cancelled = False
	def checkStatus():
		if cancelled:
			finished(False)
			return

		while True:
			try:
				if outputPipeRecv.poll(0):
					data = outputPipeRecv.recv()
					if isinstance(data, tuple):
						if data[0] == "status":
							if data[1]["target"] <= 0:
								progDialog.reset()
							else:
								progDialog.updateProgress(current=data[1]["current"], target=data[1]["target"], targetIsEstimate=False, rate=None, isDownload=True)
							progDialog.updateTask(data[1]["task"])
						elif data[0] == "error":
							qtw.QMessageBox.critical(progDialog, "Update error", f"{data[1]}\n\nIf this isn't a network-related issue, report it at https://github.com/Saju159/YTMediaTool/issues")
							finished(False)
							return
						elif data[0] == "confirmDownload":
							answer = qtw.QMessageBox.question(progDialog, "Confirm download", data[1])
							if answer == qtw.QMessageBox.StandardButton.Yes:
								inputPipeSend.send(True)
							else:
								inputPipeSend.send(False)
								finished(False)
								return
				else:
					# no data
					break
			except EOFError:
				# pipe broken
				break

		if not process.is_alive():
			r = process.exitcode
			if r == 3:
				qtw.QMessageBox.information(progDialog, "YTMediaTool", "No new release was found. You are already up-to-date.")
				finished(False)
			else:
				finished(True if r == 0 else False)
			return

		timer.start(100)

	timer = qtc.QTimer(progDialog, singleShot=True)
	timer.timeout.connect(checkStatus)
	timer.start(100)

	def cancel():
		nonlocal cancelled
		cancelled = True
		process.terminate()
	progDialog.rejected.connect(cancel)

	process.start()

	return progDialog

def Uninstall(
	parentWidget: qtw.QWidget=None
):
	answer = qtw.QMessageBox.question(parentWidget, "Confirm removal", "Are you sure you wish to remove the locally managed yt-dlp package?\n\nMake sure the system-provided package is in your Python module search path if you wish to use it!")
	if answer == qtw.QMessageBox.StandardButton.Yes:
		try:
			print("Deleting locally-managed yt-dlp package...")
			YtdlpPath.unlink()
			qtw.QMessageBox.information(parentWidget, "YTMediaTool", "Locally managed yt-dlp package deleted! Please relaunch the application.")
			qtc.QCoreApplication.instance().exit(0)
		except Exception as err:
			print(err)
			qtw.QMessageBox.critical(parentWidget, "Error", f"Error during removal:\n{err}\n\nThe application will now exit.")
			qtc.QCoreApplication.instance().exit(1)

def UpdateYtdlpPackageInfo(version, path):
	global YtdlpVersion, YtdlpImportPath
	YtdlpVersion = version
	YtdlpImportPath = path
