import os, json
from Common import getUserDownloadDir, getBaseConfigDir

Settings = {
	# Define options with their default values here
	"FFmpeg_path": "ffmpeg",
	"BasicPage-ShowDialogAfterDLSuccess": True,
	"BasicPage-DownloadDir": getUserDownloadDir(),
	"BasicPage-DLVideo": True,
	"BasicPage-DLAudio": True,
	"BasicPage-Format": "Original",
	"BasicPage-VideoQuality": "Source"
}
SettingsFilePath = os.path.join(getBaseConfigDir(), "settings.json")

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
