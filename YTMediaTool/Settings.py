import os, json
from sys import platform
from Common import getUserDownloadDir, getBaseConfigDir

# Define options with their default values here
# Keys are in tuple format:
#   [0]: default value
#   [1]: type of value
DefaultSettings = {
	"FFmpeg_path": ("ffmpeg", str),
	"BasicPage-ShowDialogAfterDLSuccess": (True, bool),
	"BasicPage-DownloadDir": (getUserDownloadDir(), str),
	"BasicPage-DLVideo": (True, bool),
	"BasicPage-DLAudio": (True, bool),
	"BasicPage-Format": ("Original", str),
	"BasicPage-VideoQuality": ("Source", str),
	"BasicPage-ForceQuality": ("Download closest to selected quality", str),
	"BasicPage-Cookies": (False, bool),
	"BasicPage-browser": ("firefox", str),
	"YDL-CookiesFilePath": ("", str),
	"YDL-EnablePlaylistDL": (False, bool),
	"YDL-SkipIfExists": (False, bool),
	"YDL-MaxNumberOfRetries": (10, int), # unimplemented
	"YDL-DLFilenameTemplate": ("%(title).165B.%(ext)s", str), # "%(title).165B [%(id)s].%(ext)s"
	"SMLD-mutithreading": (4, int),
	"SMLD-source": ("YouTube Music", str),
	"SMLD-useytmetadata": (True, bool),
	"SMLD-structure":  ("/ARTIST/ALBUM/SONG", str)
}
SettingsFilePath = os.path.join(getBaseConfigDir(), "settings.json")

# Current setting values
Settings = {}

for key, setting in DefaultSettings.items():
	Settings[key] = setting[0]

def setSetting(key: str, val):
	if not key in Settings:
		print(f"Attempted to set value of invalid setting \"{key}\" to \"{val}\"!")
		return False

	if isinstance(val, DefaultSettings[key][1]):
		Settings[key] = val
		return True
	else:
		print(f"Attempted to set value \"{val}\" with type \"{val.__class__}\" to setting \"{key}\", which only accepts \"{DefaultSettings[key][1]}\" values!")
		return False

def resetSetting(key: str):
	Settings[key] = DefaultSettings[key][0]

if platform == "linux":
	# Set default FFmpeg path on linux to use the system installed one
	setSetting("FFmpeg_path", "/usr/bin/ffmpeg")

def loadSettingsFromFile():
	print(f"Loading settings from '{SettingsFilePath}'...")
	if os.path.isfile(SettingsFilePath):
		with open(SettingsFilePath, "r") as settingsFile:
			loadedSettings = json.loads(settingsFile.read())
			for key in loadedSettings:
				if key in Settings:
					setSetting(key, loadedSettings[key])

def saveSettingsToFile():
	print(f"Saving settings to '{SettingsFilePath}'...")
	with open(SettingsFilePath, "w") as settingsFile:
		settingsFile.write(json.dumps(Settings))

loadSettingsFromFile()
