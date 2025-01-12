import multiprocessing, os, pathlib, subprocess
from sys import platform
import tkinter as tk
from tkinter import filedialog

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

def openFilePicker(window: tk.Tk, dtype: str, **kwargs):
	window.update() # Prevent program from freezing if root window is killed while file picker is open
	title = "title" in kwargs and kwargs["title"] or None

	if platform == "linux":
		# Use kdialog if installed on linux for a better file picker.
		# Will check if kdialog is installed and if not, fallback to tkinter file picker for compatibility
		kdialog_installed = subprocess.run(["which", "kdialog"], stdout=subprocess.PIPE)
		if kdialog_installed.returncode == 0:
			pickerargs = ["kdialog"]
			if title:
				pickerargs.append("--title")
				pickerargs.append(title)

			if dtype == "openDir": pickerargs.append("--getexistingdirectory")
			elif dtype == "openFile": pickerargs.append("--getopenfilename")
			elif dtype == "saveFile": pickerargs.append("--getsavefilename")
			else: raise Exception("Invalid dtype! Must be 'openDir', 'openFile' or 'saveFile'")

			c = subprocess.run(pickerargs, stdout=subprocess.PIPE, encoding="utf-8")
			if c.returncode == 0:
				pathStr = str(c.stdout)[:-1]
				return pathStr
			else:
				return None

	# Fallback to tkinter picker (native on windows)
	picked = None
	if dtype == "openDir": picked = filedialog.askdirectory(parent=window, title=title, mustexist=True)
	elif dtype == "openFile": picked = filedialog.askopenfilename(parent=window, title=title)
	elif dtype == "saveFile": picked = filedialog.asksaveasfilename(parent=window, title=title)
	else: raise Exception("Invalid dtype! Must be 'openDir', 'openFile' or 'saveFile'")
	window.update()

	if picked and len(picked) > 0: return picked
	else: return None

tmpPath = pathlib.PurePath(getBaseConfigDir(), "YDL_temp")
def ydlProcessTarget(returnPipe, queue, url, path, fileformat, dlvideo, dlaudio, videoquality):
	import Info, math
	from Settings import Settings
	from yt_dlp import YoutubeDL

	print(f"Downloading \"{url}\" to \"{path}\"...")
	if len(url) <= 0: print("Invalid url"); returnPipe.send(("invalidDownloadInput")); return
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
					"downloaded_bytes": downloaded_bytes
				}

				if 'total_bytes' in d:
					datatable["total_bytes"] = d['total_bytes']
				elif 'total_bytes_estimate' in d:
					datatable["total_bytes"] = d['total_bytes_estimate']
					datatable["total_bytes_is_estimate"]: True

				if 'speed' in d:
					datatable["speed"] = d["speed"]

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
		'outtmpl': {'default': "%(title).165B [%(id)s].%(ext)s"},
		'paths': {'home': str(path), 'temp': str(tmpPath)},
		'overwrites': True, # FIXME: workaround for ffmpeg failure if already downloaded
		'continuedl': False,
		'updatetime': False, # Don't set file modification timestamp to video upload time
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

	if Settings["BasicPage-Cookies"]:
		cookies = (Settings["BasicPage-browser"])
		opts["cookiesfrombrowser"] = (cookies, None, None, None)

	with YoutubeDL(opts) as ydl:
		try:
			c = ydl.download(url)
			if final_file_path and "ext" in ff:
				# Fix the file path to use correct file ext since yt_dlp only gives the original pre-conversion file path
				final_file_path = os.path.splitext(final_file_path)[0]+"."+ff["ext"]

			print(f"return code: {c}")
			print(f"filepath: {final_file_path}")
			if dlvideo and "res" in vq and Settings["BasicPage-ForceQuality"] == "Resize to selected quality" and "ffmpeg_location" in opts:
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

if __name__ == "__main__" and platform == "linux":
	multiprocessing.set_start_method("fork")
