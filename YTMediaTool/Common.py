import multiprocessing, os, pathlib, subprocess
from sys import platform
import PySide6.QtWidgets as qtw

class DownloadError(Exception):
	def __init__(self, errors=str, reason=str):
		self.errors = errors
		self.reason = reason

def getUserDownloadDir():
	if platform == "linux":
		c = subprocess.run(["which", "xdg-user-dir"], stdout=subprocess.PIPE)
		if c.returncode == 0:
			c = subprocess.run(["xdg-user-dir", "DOWNLOAD"], capture_output=True, encoding="utf-8")
			if c.returncode == 0:
				pathStr = str(c.stdout)[:-1]
				return pathStr

	# fallback to a 'Downloads' directory in the user's home
	return os.path.expanduser("~/Downloads")

def getBaseConfigDir():
	configPath = "~/.YTMediaTool/" # Fallback if not linux or windows
	if platform == "linux":
		configPath = os.environ.get('XDG_CONFIG_HOME') and os.path.join(os.environ.get('XDG_CONFIG_HOME'), "YTMediaTool/") or "~/.config/YTMediaTool/"
	elif platform == "win32":
		configPath = "~\\AppData\\Roaming\\YTMediaTool"

	configPath = os.path.expanduser(configPath)
	#print("Config path: "+configPath)
	if not os.path.exists(configPath):
		print("Config dir doesn't exist! Creating...")
		os.makedirs(configPath)
	return configPath

def openDirInFileBrowser(directory: str):
	if platform == "linux":
		c = subprocess.run(["which", "xdg-open"], stdout=subprocess.PIPE)
		if c.returncode == 0:
			subprocess.run(["xdg-open", directory], stdout=subprocess.PIPE)
		else:
			print("xdg-open not found! Can't open directory in system file browser!")
	elif platform == "win32":
		subprocess.run(["explorer", os.path.normpath(directory)], stdout=subprocess.PIPE)

def openFilePicker(window: qtw.QWidget, dtype: str, **kwargs):
	title = "title" in kwargs and kwargs["title"] or None

	picked = None
	if dtype == "openDir": picked = qtw.QFileDialog.getExistingDirectory(window, title)
	elif dtype == "openFile": picked = qtw.QFileDialog.getOpenFileName(window, title)[0]
	elif dtype == "saveFile": picked = qtw.QFileDialog.getSaveFileName(window, title)[0]
	else: raise Exception("Invalid dtype! Must be 'openDir', 'openFile' or 'saveFile'")
	window.update()

	if picked and len(picked) > 0: return picked
	else: return None

tmpPath = pathlib.PurePath(getBaseConfigDir(), "YDL_temp")
def ydlProcessTarget(returnPipe, queue, url, path, fileformat, dlvideo, dlaudio, videoquality):
	import Info
	from Settings import Settings
	from yt_dlp import YoutubeDL

	print(f"Downloading \"{url}\" to \"{path}\"...")
	if len(url) <= 0 or url == "ytsearch:": print("Invalid url"); returnPipe.send(("invalidDownloadInput")); return
	if len(str(path)) <= 0: print("Invalid path"); returnPipe.send(("invalidDirectory")); return
	if not os.path.isdir(path): print("Path does not point to a directory!"); returnPipe.send(("pathIsNotDir")); return
	if not fileformat in Info.fileformats: print("Invalid fileformat"); returnPipe.send(("invalidff")); return
	if not videoquality in Info.videoqualities: print("Invalid video quality"); returnPipe.send(("invalidvq")); return

	ff = Info.fileformats[fileformat]
	vq = Info.videoqualities[videoquality]

	final_file_path = None
	dlQuality = None
	def progress_hook(d):
		try:
			nonlocal final_file_path, dlQuality
			if d['status'] == "downloading":
				downloaded_bytes = d['downloaded_bytes']
				datatable = {
					"phase": "download",
					"progressWindowLabel": "Downloading...",
					"downloaded_bytes": float(downloaded_bytes)
				}

				if 'total_bytes' in d:
					datatable["total_bytes"] = float(d['total_bytes'])
				elif 'total_bytes_estimate' in d:
					datatable["total_bytes"] = float(d['total_bytes_estimate'])
					datatable["total_bytes_is_estimate"]: True

				if 'speed' in d:
					datatable["speed"] = float(d["speed"])

				try: queue.get(False)
				except: pass
				queue.put(datatable, False)

			elif d['status'] == "finished":
				final_file_path = d.get("info_dict").get("_filename")
				try: queue.get(False)
				except: pass
				queue.put({
					"phase": "postprocess",
					"progressWindowLabel": "Postprocessing..."
				}, False)

			if d.get("info_dict").get("height"):
				dlQuality = str(d.get("info_dict").get("height"))

		except Exception as err:
			print("Error in progress hook:\n"+str(err))

	opts = {
		'verbose': False,
		'outtmpl': {'default': Settings["YDL-DLFilenameTemplate"]},
		'paths': {'home': str(path), 'temp': str(tmpPath)},
		'overwrites': not Settings["YDL-SkipIfExists"], # FIXME: workaround for ffmpeg failure if already downloaded
		'continuedl': False,
		'restrictfilenames': True,
		'updatetime': False, # Don't set file modification timestamp to video upload time
		'noplaylist': not Settings["YDL-EnablePlaylistDL"],
		'color': {'stderr': 'never', 'stdout': 'never'},
		'progress_hooks': [progress_hook]
	}

	if "FFmpeg_path" in Settings:
		opts["ffmpeg_location"] = Settings["FFmpeg_path"]

	if ff["video"] == False: dlvideo = False
	if ff["audio"] == False: dlaudio = False

	if dlvideo and dlaudio:
		opts["format"] = "bv*+ba/b"
	elif dlvideo and not dlaudio:
		opts["format"] = "bv"
	elif not dlvideo and dlaudio:
		opts["format"] = "ba"
	else:
		print("No video or audio selected")
		returnPipe.send(("noVideoOrAudio")); return

	if "ext" in ff:
		ext = ff["ext"]
		opts['final_ext'] = ext
		opts['postprocessors'] = [{'key': 'FFmpegVideoConvertor', 'preferedformat': ext}]

	if dlvideo and "res" in vq:
		opts['format_sort'] = [f'res:{vq["res"]}']

	if len(Settings["YDL-CookiesFilePath"]) > 2:
		print("Using cookie file!")
		opts["cookiefile"] = str(Settings["YDL-CookiesFilePath"])
	elif Settings["BasicPage-Cookies"]:
		browser_to_grab_from = (Settings["BasicPage-browser"])
		print(f"Grabbing cookies from {browser_to_grab_from}!")
		opts["cookiesfrombrowser"] = (browser_to_grab_from, None, None, None)

	with YoutubeDL(opts) as ydl:
		try:
			c = ydl.download(url)
			if final_file_path and "ext" in ff:
				# Fix the file path to use correct file ext since yt_dlp only gives the original pre-conversion file path
				final_file_path = os.path.splitext(final_file_path)[0]+"."+ff["ext"]

			print(f"return code: {c}")
			print(f"filepath: {final_file_path}")
			if final_file_path and dlvideo and "res" in vq and Settings["BasicPage-ForceQuality"] == "Resize to selected quality" and "ffmpeg_location" in opts:
				if os.path.isfile(opts["ffmpeg_location"]) and str(dlQuality) != str(vq["res"]):
					try: queue.get(False)
					except: pass # empty the queue
					queue.put({
						"phase": "resize",
						"progressWindowLabel": "Resizing..."
					}, False)

					ffmpeg_path = opts["ffmpeg_location"]

					if not final_file_path:
						print("No file path reported!")
						returnPipe.send(("unknownException", "Video was downloaded but not resized!\nyt-dlp did not report a file path for FFmpeg post processing!")); return

					fname, fext = os.path.split(final_file_path)
					ffmpeg_cmd = subprocess.run([
						ffmpeg_path,
						"-i", final_file_path,
						"-vf", f"scale=-2:{vq["res"]}",
						"-c:a", "copy",
						"-y",
						f"{fname}/.RESIZE.{fext}"
					])
					if ffmpeg_cmd.returncode == 0:
						os.replace(f"{fname}/.RESIZE.{fext}", final_file_path)
					else:
						if not final_file_path:
							print("Error during postprocessing!")
							returnPipe.send(("unknownException", "Error during video resizing!")); return
		except Exception as err:
			print("--- Exception in ydl.download() ---\n"+str(err))
			returnPipe.send(("unknownException", str(err))); return
			# return "unknownException", err

		returnPipe.send(("success")); return

def createYDLProcess(
	url: str,
	path: str,
	fileformat: str = "Original",
	dlvideo: bool = True,
	dlaudio: bool = True,
	videoquality: str = "Source"
):
	print(f"Creating YDL process for url: \"{url}\"...")
	path = pathlib.PurePath(path)
	pathlib.Path(path).mkdir(parents=True, exist_ok=True)
	pathlib.Path(tmpPath).mkdir(parents=True, exist_ok=True)

	returnPipeReceiver, returnPipeSender = multiprocessing.Pipe(False)
	statusQueue = multiprocessing.Queue(1)
	process = multiprocessing.Process(target=ydlProcessTarget, args=(returnPipeSender, statusQueue, url, path, fileformat, dlvideo, dlaudio, videoquality))

	return process, returnPipeReceiver, statusQueue

def downloadFile(
	url: str,
	path: pathlib.Path,
	maxlength: int = 0,
	sha256: str = None,
	statusCallback: callable = None,
):
	"""
	Downloads a file to specified path.

	Data is written to a file with the same name but with the .part extension.

	After fully downloaded, the file is moved to the correct path.

	Delete the .part file if cancelled (e.g. by killing the child process this function was running in)

	:param maxlength: Maximum amount of data to be downloaded. 0=infinite
	:param sha256: SHA256 hash to check agaisnt. None=no verification
	:param statusCallback: Will be called on progress update with the parameters "task", "current", "target"
	:raise DownloadError: Raised on URLError and verification failure
	"""
	import hashlib
	import shutil
	import urllib.error
	import urllib.request

	print(f"Downloading file from \"{url}\" to \"{path}\"...")

	pathlib.Path(path).parent.mkdir(parents=True, exist_ok=True)
	partPath = pathlib.Path(path.parent, path.name+".part")
	partPath.unlink(missing_ok=True)

	def pushStatus(task, current=0, target=0):
		if statusCallback != None:
			statusCallback(task=task, current=current, target=target)

	try:
		with urllib.request.urlopen(url, None, 30) as r:
			dinfo = r.info()
			dl_len = (int(dinfo["Content-Length"]) if "Content-Length" in dinfo else 0) or 0
			chunk_size = 65536 # read in 64kb chunks

			with partPath.open("wb") as f:
				times = 0
				while True:
					if maxlength != 0 and times*chunk_size > maxlength:
						# over max length to download, break
						break
					data = r.read(chunk_size)
					if not data:
						break
					times += 1
					pushStatus(task="downloading", current=times*chunk_size, target=max(dl_len, maxlength) if dl_len != 0 else 0)
					f.write(data)

		if sha256 != None:
			pushStatus(task="verifying")

			with partPath.open("rb") as data:
				h = hashlib.sha256()
				h.update(data.read())
				digest = h.hexdigest()
				if digest != sha256:
					# sha256 didn't match so delete file and return error
					partPath.unlink()
					raise DownloadError("wrongDigest", f"Downloaded file has wrong SHA256 hash:\n\n     got: {digest}\nexpected: {sha256}")

		# sha256 matched or no sha256 passed, so move file to correct path and return success
		pushStatus(task="moving")

		shutil.move(partPath, path)
		print(f"Successfully downloaded file from \"{url}\" to \"{path}\"!")
		return

	except urllib.error.URLError as e:
		partPath.unlink(missing_ok=True)
		raise DownloadError("urlError", e.reason)

def cleanupYDLTemp():
	for f in os.listdir(tmpPath):
		if os.path.isfile(os.path.join(tmpPath, f)):
			os.remove(os.path.join(tmpPath, f))
	print("Cleaned up YDL temp directory!")

def isVersionNewer(a: str, b: str):
	"""
	Returns True if version str a is higher than b
	"""
	apart = a.split(".")
	bpart = b.split(".")

	for i in range(len(apart)):
		if len(bpart) > i:
			inta, intb = int(apart[i]), int(bpart[i])
			if inta and intb:
				if inta > intb:
					return True
				if inta < intb:
					return False
			else:
				return True

	return False

if __name__ == "__main__" and platform == "linux":
	multiprocessing.set_start_method("fork")
