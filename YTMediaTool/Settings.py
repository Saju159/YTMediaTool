import os, json
from sys import platform
from Common import getUserDownloadDir, getBaseConfigDir

Settings = {
	# Define options with their default values here
	"FFmpeg_path": "ffmpeg",
	"BasicPage-ShowDialogAfterDLSuccess": True,
	"BasicPage-DownloadDir": getUserDownloadDir(),
	"BasicPage-DLVideo": True,
	"BasicPage-DLAudio": True,
	"BasicPage-Format": "Original",
	"BasicPage-VideoQuality": "Source",
	"BasicPage-ForceQuality": "Download closest to selected quality",
	"BasicPage-Cookies": False,
	"BasicPage-browser": "firefox",
	"YDL-CookiesFilePath": "",
	"YDL-EnablePlaylistDL": False,
	"YDL-SkipIfExists": False,
	"YDL-MaxNumberOfRetries": 10 # unimplemented
}
SettingsFilePath = os.path.join(getBaseConfigDir(), "settings.json")

if platform == "linux":
	# Set default FFmpeg path on linux to use the system installed one
	Settings["FFmpeg_path"] = "/usr/bin/ffmpeg"

def loadSettingsFromFile():
	print(f"Loading settings from '{SettingsFilePath}'...")
	if os.path.isfile(SettingsFilePath):
		with open(SettingsFilePath, "r") as settingsFile:
			loadedSettings = json.loads(settingsFile.read())
			for key in loadedSettings:
				if key in Settings:
					Settings[key] = loadedSettings[key]

def saveSettingsToFile():
	print(f"Saving settings to '{SettingsFilePath}'...")
	with open(SettingsFilePath, "w") as settingsFile:
		settingsFile.write(json.dumps(Settings))

loadSettingsFromFile()
