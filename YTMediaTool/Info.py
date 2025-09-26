fileformats = {
	'Original':	{'video': True, 'audio': True},
	'MP4':	{'video': True, 'audio': True, 'ext': "mp4"},
	'M4A':	{'video': False, 'audio': True, 'ext': "m4a"},
	'Matroska (mkv)':	{'video': True, 'audio': True, 'ext': "mkv"},
	'WebM':	{'video': True, 'audio': True, 'ext': "webm"},
	'MP3':	{'video': False, 'audio': True, 'ext': "mp3"},
	'Ogg':	{'video': False, 'audio': True, 'ext': "ogg"},
	'QuickTime (mov)':	{'video': True, 'audio': True, 'ext': "mov"},
	'Theora (ogv)':	{'video': True, 'audio': True, 'ext': "ogv"},
	'WAV':	{'video': False, 'audio': True, 'ext': "wav", 'warn': "WAV files are uncompressed and will result in very large files!"},
}

videoqualities = {
	'Source': {},
	'2160p (4K)': {'res': 2160},
	'1440p': {'res': 1440},
	'1080p (FHD)': {'res': 1080},
	'720p (HD)': {'res': 720},
	'480p': {'res': 480},
	'360p': {'res': 360},
	'288p': {'res': 288},
	'240p': {'res': 240},
	'144p': {'res': 144},
}

urlregex = "^(https?:\\/\\/)([a-zA-Z0-9_\\-\\.]+)(\\/|)([a-zA-Z0-9_\\/\\-\\.%?=#\\[\\]@!&$:~,;']+)?"

filenametemplates = {
	"Title.ext": "%(title).165B.%(ext)s",
	"Title [source ID].ext": "%(title).165B [%(id)s].%(ext)s"
}
