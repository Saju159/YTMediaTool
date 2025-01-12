fileformats = {
	'Original':	{'video': True, 'audio': True},
	'MP4':	{'video': True, 'audio': True, 'ext': "mp4"},
	'M4A':	{'video': False, 'audio': True, 'ext': "m4a"},
	'WebM':	{'video': True, 'audio': True, 'ext': "webm"},
	'MP3':	{'video': False, 'audio': True, 'ext': "mp3"},
	'Ogg':	{'video': False, 'audio': True, 'ext': "ogg"},
	'FLAC':	{'video': False, 'audio': True, 'ext': "flac", 'warn': "Downloading to FLAC does not magically make your audio high-quality, as audio is almost always converted from a lossy format to this!"},
	'WAV':	{'video': False, 'audio': True, 'ext': "wav", 'warn': "WAV files are uncompressed and will result in very large files! Use with caution."},
	'Theora (ogv)':	{'video': True, 'audio': True, 'ext': "ogv"},
	'Matroska (mkv)':	{'video': True, 'audio': True, 'ext': "mkv"},
	'QuickTime Movie (mov)':	{'video': True, 'audio': True, 'ext': "mov"}
}

videoqualities = {
	'Source': {},
	'2160p (4K)': {'res': 2160},
	'1440p': {'res': 1440},
	'1080p (FHD)': {'res': 1080},
	'720p': {'res': 720},
	'480p': {'res': 480},
	'360p': {'res': 360},
	'288p': {'res': 288},
	'240p': {'res': 240},
	'144p': {'res': 144},
	'72p': {'res': 72}
}
