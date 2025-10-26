import os
from mutagen.mp4 import MP4
import os.path
from yt_dlp import YoutubeDL
from Settings import Settings
from Common import getBaseConfigDir
import ytmusicapi
import SMLDprogressTracker
import threading
import SMLDpage
import requests
import time
from datetime import datetime

diagnosis = 1 #1 = on, 0 = off

#filetypes: 1 = itunes, 2 = spotify or itunes lite, 3 = quick download format
startrunloop_after_setup = True #default true, stop loop from running after setup when false
enable_yt_output = False #enable YT-DLP output printing

filter = '?ü"[];:,.()®*\'é' #global filter for song album and artist names
filter3 = '?ü"[];:,()®*\'é'

global ratelimited, smlderror, filenotfound, cancel
global libraryfiledirectory, libraryfiledirectory, downloaddirectory, fileformat
global donelist
donelist = [False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False]

fileformat = ""
libraryfiledirectory = ""
downloaddirectory = ""
ratelimited = False
smlderror = False
filenotfound = False
failalert = False

def clearlog():
	with open(os.path.join(getBaseConfigDir(),"SMLD","SMLDlog.txt"), 'w') as log:
		log.write("")
		log.close()
	if diagnosis == 1:
		print("Log cleared")

def getinfo():
	if diagnosis == 1:
		print(f"Download Directory: {downloaddirectory}")
		print(f"Library location: {libraryfiledirectory}")
		print("info acquired")

def getstructure(artist, albumname, songname, fileformat):
	structure = Settings["SMLD-structure"]
	if structure == "/SONG":
		return f"{songname}.{fileformat}"

	elif structure == "/ALBUM/SONG":
		return os.path.join(albumname, f"{songname}.{fileformat}")

	elif structure == "/ARTIST/SONG":
		return os.path.join(artist,f"{songname}.{fileformat}")

	elif structure == "/ARTIST ALBUM/SONG":
		return os.path.join(f"{artist} {albumname}", f"{songname}.{fileformat}")

	elif structure == "/ARTIST/ALBUM/SONG":
		return os.path.join(artist,albumname,f"{songname}.{fileformat}")

	else:
		if diagnosis == 1:
			addlogentry('File structure is invalid. In function "getstructure".')
			print("File structure is invalid.")
		raise Exception("File structure is invalid.")

def addlogentry(logentry):
	with open(os.path.join(getBaseConfigDir(),"SMLD","SMLDlog.txt"), 'a', encoding='utf-8') as log:
		try:
			log.write(f"{logentry} at  {datetime.now()} with list {libraryfiledirectory}")
			log.write("\n")
		except:
			print("Error while trying to write error log.")
		log.close()

def downloadfail():
	with open(os.path.join(getBaseConfigDir(),"SMLD", "Temp","SMLDfail.txt"), 'a', encoding='utf-8') as log:
		try:
			log.write(f"Fail at  {datetime.now()} with list {libraryfiledirectory}")
			log.write("\n")
		except:
			print("Error while trying to write error log.")

def checkfails():
	global failalert, cancel
	with open(os.path.join(getBaseConfigDir(),"SMLD", "Temp", "SMLDfail.txt"), 'r', encoding='utf-8') as file:
		fails = len(file.readlines())
		file.close()
	if fails > 10:
		failalert = True

		cancel = True

def emptyfails():
	with open(os.path.join(getBaseConfigDir(),"SMLD", "Temp", "SMLDfail.txt"), 'w', encoding='utf-8') as f:
		f.write("")
		f.close


def removeline(filteredsongline, threadnumber):
	if filteredsongline:  # Ohitetaan tyhjät rivit
		# Päivitetään tiedosto ilman ensimmäistä riviä
		with open(os.path.join(getBaseConfigDir(),"SMLD", "Temp", "Songlist" + str(threadnumber) + ".txt"), 'r') as tiedosto:
			songlistlines = tiedosto.readlines()
			tiedosto.close()
		jäljellä_olevat_rivit = songlistlines[1:]  # Jäljellä olevat rivit

		tiedostonimi = os.path.join(getBaseConfigDir(),"SMLD", "Temp", "Songlist" + str(threadnumber) + ".txt")
		with open(tiedostonimi, 'w', encoding='utf-8') as tiedosto:
			tiedosto.writelines(jäljellä_olevat_rivit)
		if diagnosis == 1:
			print("Ensimmäinen rivi poistettu.")
		return tiedostonimi


def dividesonglist():
	threadcount = int(Settings["SMLD-mutithreading"])

	with open(os.path.join(getBaseConfigDir(), "SMLD", "Temp", "Songlist.txt"), 'r', encoding='utf-8') as f:
		originallines = f.readlines()

	print(f"Kokonaisrivit: {len(originallines)}")

	start = 0
	for songlistnumber in range(threadcount):
		total_lines = len(originallines)
		lines_per_part = total_lines // threadcount
		remainder = total_lines % threadcount

		extra_line = 1 if songlistnumber < remainder else 0
		end = start + lines_per_part + extra_line

		part_filename = os.path.join(getBaseConfigDir(), "SMLD", "Temp", f"Songlist{songlistnumber}.txt")
		print(f"Tiedosto {songlistnumber}: start={start}, end={end}, tiedostoon: {part_filename}")

		with open(part_filename, 'w', encoding='utf-8') as part_file:
			lines_to_write = originallines[start:end]
			print(f"Kirjoitetaan {len(lines_to_write)} riviä tiedostoon {part_filename}")  # Näyttää kuinka monta riviä kirjoitetaan
			part_file.writelines(lines_to_write)
		start = end
	print(f"Tiedosto jaettu {threadcount} osaan.")

def createsonglist():
	try:
		with open(libraryfiledirectory, 'r', encoding='utf-8') as tiedosto:
			ensimrivi = tiedosto.readlines(1)

		global filetype
		#filetype = str(libraryfiledirectory).find(".txt")

		if libraryfiledirectory.lower().endswith(".txt"):
			if "Quick Download" in str(libraryfiledirectory):
				filetype = 3
			else:
				filetype = 1
		else:
			filetype = 2

		if diagnosis == 1:
			print("Filetype is: " + str(filetype))

		with open(libraryfiledirectory, 'r', encoding='utf-8') as tiedosto:
			rivit2 = tiedosto.readlines()

		if filetype == 1:
			if diagnosis == 1:
				print("Selected file is a iTunes media library. With .txt file format")

			with open((os.path.join(getBaseConfigDir(),"SMLD", "Temp", "Songlist.txt")), 'w', encoding='utf-8') as tiedosto:
				for txtrivi in rivit2:
					txtosat = txtrivi.split('\t')  # Käytetään kahta tabulaattoria erottimena
					if len(txtosat) > 4:  # Tarkistetaan, että riittävästi osia löytyy
						uusi_txtrivi = f"{txtosat[0]}\t{txtosat[3]}\t{txtosat[4]}\t{txtosat[5]}\t{txtosat[6]}\n"  # Ensimmäinen ja kolmas osa
						tiedosto.write(uusi_txtrivi)
			if diagnosis == 1:
				print("File saved successfully.")
		elif filetype == 2:
			if diagnosis == 1:
				print("Selected file is a iTunes or Spotify media library.")
			with open((os.path.join(getBaseConfigDir(),"SMLD", "Temp", "Songlist.txt")), 'w', encoding='utf-8') as tiedosto:
				for csvrivi in rivit2:
					csvosat = csvrivi.split(',')
					if len(csvosat) > 2:  # Tarkistetaan, että riittävästi osia löytyy
						uusi_csvrivi = f"{csvosat[0]},{csvosat[1]},{csvosat[2]}\n"
						tiedosto.write(uusi_csvrivi)

			delete = str(ensimrivi).find("Track name") #Delete the first line if it contains header line "Track name"
			if not delete == -1:
				with open(os.path.join(getBaseConfigDir(),"SMLD", "Temp", "Songlist.txt"), 'r') as fin:
					data = fin.read().splitlines(True)
				with open(os.path.join(getBaseConfigDir(),"SMLD", "Temp", "Songlist.txt"), 'w') as fout:
					fout.writelines(data[1:])

				if diagnosis == 1:
					print("Header line removed")
		elif filetype == 3:
			with open((os.path.join(getBaseConfigDir(),"SMLD", "Temp", "Songlist.txt")), 'w', encoding='utf-8') as tiedosto:
				tiedosto.write("")

			if diagnosis == 1:
				print("Selected file is a quick download format.")
				print(rivit2)

		rivit3 = []

		for entry in rivit2[1:]:
			parts = entry.split(',')
			artist = parts[0]
			songs = parts[1:]

			for song in songs:
				rivit3.append(f"{artist},{song}")

		with open(os.path.join(getBaseConfigDir(), "SMLD", "Temp", "Songlist.txt"), 'a', encoding='utf-8') as tiedosto:
			for line in rivit3:
				line_cleaned = line.strip().replace("'", "")
				print("Kirjoitetaan:", line_cleaned)
				tiedosto.write(line_cleaned + "\n")

		if diagnosis == 1:
			print("File saved successfully.")
	except Exception as e:
		print(f"An error occured231: {e}")
		global smlderror
		smlderror = True
		addlogentry("Error: " + str(e))
	#Delete empty lines:
	with open(os.path.join(getBaseConfigDir(),"SMLD", "Temp", "Songlist.txt"), 'r', encoding='utf-8') as file:
		lineswithempty = file.readlines()
	non_empty_lines = [line for line in lineswithempty if line.strip()]
	with open(os.path.join(getBaseConfigDir(),"SMLD", "Temp", "Songlist.txt"), 'w', encoding='utf-8') as file:
		file.writelines(non_empty_lines)
		file.close()

def getsonginfo(threadnumber):
	global artisttoshow, songnametoshow, albumnametoshow
	with open(os.path.join(getBaseConfigDir(),"SMLD", "Temp", "Songlist" + str(threadnumber) + ".txt"), 'r') as tiedosto:
		 songlistlines = tiedosto.readlines()
	# Ota ensimmäinen rivi ja poista se tiedoston riveistä

	if not songlistlines == "":
		filteredsongline = songlistlines[0].strip()  # Poista rivin ympäriltä tyhjät merkit
	else:
		print ("Thread" + str(threadnumber) +"file is empty")

	songlinefilter = "/?ü().:"
	for char in songlinefilter:
		filteredsongline = filteredsongline.replace(char, "")

	if not songlistlines == "":   #if songlist contains something, continue
		if filetype == 1:
			if diagnosis == 1:
				print("Expanded iTunes format")
			txtparts = filteredsongline.split('\t')
			if len(txtparts) > 2:
				songname = f"{txtparts[0]}"
				artist = f"{txtparts[1]}"
				albumname2 = f"{txtparts[2]}"
				albumname1 = albumname2.replace(")", "")
				albumname = albumname1.replace("(", "")
				rating = f"{txtparts[4]}"

				artisttoshow = artist
				songnametoshow = songname
				albumnametoshow = albumname
		elif filetype == 2:
			if diagnosis == 1:
				print("Spotify or iTunes lite.")
			csvparts = filteredsongline.split(',')
			songname = f"{csvparts[1]}"
			for char in filter:
				songname = songname.replace(char, "")
			artist = f"{csvparts[2]}"
			for char in filter:
				artist = artist.replace(char, "")
			#albumname = getmoremetadata(threadnumber, songname, artist)
			albumname = ""
			for char in filter:
				albumname = albumname.replace(char, "")
			rating = ""  #set rating to none as csv does not contain rating data
			artisttoshow = artist
			songnametoshow = songname
			albumnametoshow = albumname

		elif filetype == 3:
			if diagnosis == 1:
				print("Quick download format detected. Taking metadata from YT Music")
			cusparts = filteredsongline.split(',')
			songname = f"{cusparts[1]}"
			for char in filter:
				songname = songname.replace(char, "")
				songname = songname.strip()
			artist = f"{cusparts[0]}"
			for char in filter:
				artist = artist.replace(char, "")
				artist = artist.strip()
			rating = ""  #set rating to none as csv does not contain rating data

			albumname = getmoremetadata(threadnumber, songname, artist)
			artisttoshow = artist
			songnametoshow = songname
			albumnametoshow = albumname

	if diagnosis == 1:
		print ("Artist: " + artist)
	songfilewithoutformat = os.path.join(downloaddirectory, getstructure(artist, albumname, songname, fileformat))
	for char in filter3:
		songfilewithoutformat = songfilewithoutformat.replace(char, "")
	if diagnosis == 1:
		print("Lopullinen tiedosto on: " + songfilewithoutformat)

	return albumname, songname, artist, songfilewithoutformat, filteredsongline, rating

def addtoplaylists(threadnumber):
	albumname, songname, artist, songfilewithoutformat, filteredsongline, rating = getsonginfo(threadnumber)
	currentdownloadplaylist = (os.path.join(downloaddirectory, "CurrentDownload.m3u" ))
	favoritesplaylist = (os.path.join(downloaddirectory, "Favorites.m3u" ))
	with open(currentdownloadplaylist, 'a', encoding='utf-8') as playlist:
		playlist.write(getstructure(artist, albumname, songname, fileformat))
		playlist.write("\n")
		playlist.close()
		if diagnosis == 1:
			print("Current download playlist written")

	if rating == "2":
		with open(favoritesplaylist, 'a', encoding='utf-8') as playlist:
			playlist.write(getstructure(artist, albumname, songname, fileformat))
			playlist.write("\n")
			playlist.close()

def setupplaylists():
	global currentdownloadplaylist, favoritesplaylist
	currentdownloadplaylist = (os.path.join(downloaddirectory, "CurrentDownload.m3u" ))
	with open(currentdownloadplaylist, 'w', encoding='utf-8') as f2:
		f2.write("#EXTM3U")
		f2.write("\n")
		f2.close()

	if filetype == 1:
		favoritesplaylist = (os.path.join(downloaddirectory, "Favorites.m3u" ))

		with open(favoritesplaylist, 'w', encoding='utf-8') as f2:
			f2.write("#EXTM3U")
			f2.write("\n")
			f2.close()
		if diagnosis == 1:
			print("Playlists were setup")

def setytoptions(threadnumber):
	albumname, songname, artist, songfilewithoutformat, filteredsongline, rating = getsonginfo(threadnumber)
	if diagnosis == 1:
		print("Download location: " + songfilewithoutformat)
	ytoptions = {
	'format': 'bestaudio',
	'max_downloads': 1,
	'outtmpl': {'default': os.path.join(downloaddirectory, getstructure(artist, albumname, songname, fileformat))},
	'final_ext' : fileformat,
	'postprocessors' : [{'key': 'FFmpegVideoConvertor', 'preferedformat': fileformat}],
	}
	if enable_yt_output:
		ytoptions['quiet']= False
		ytoptions['noprogress']= False
	else:
		ytoptions['quiet']= True
		ytoptions['noprogress']= True
	if "FFmpeg_path" in Settings:
		ytoptions["ffmpeg_location"] = Settings["FFmpeg_path"]
	if len(Settings["YDL-CookiesFilePath"]) > 2:
		if diagnosis == 1:
			print("Using cookie file!")
		ytoptions["cookiefile"] = str(Settings["YDL-CookiesFilePath"])
	elif Settings["BasicPage-Cookies"]:
		browser_to_grab_from = (Settings["BasicPage-browser"])
		if diagnosis == 1:
			print(f"Grabbing cookies from {browser_to_grab_from}!")
		ytoptions["cookiesfrombrowser"] = (browser_to_grab_from, None, None, None)
	if diagnosis == 1:
		print("YT options were set")
	return ytoptions

def yterror(e, artist, albumname, songname, threadnumber):
	albumname, songname, artist, songfilewithoutformat, filteredsongline, rating = getsonginfo(threadnumber)
	if "Sign in to confirm your age." in str(e):
		addlogentry(f"Failed to download: {getstructure(artist, albumname, songname, fileformat)} Video is age-restricted. Enabling browser cookies in the settings might help. Skipping this song.")
		if diagnosis == 1:
			print("Song is age restricted. Skipping...")
		removeline(filteredsongline, threadnumber)

	if "Sign in to confirm you’re not a bot." in str(e):
		global ratelimited
		ratelimited = True
		addlogentry(f"Failed to download: {getstructure(artist, albumname, songname, fileformat)} You are probably rate limited. Enabling browser cookies in the settings might help.")

	elif "Postprocessing: Error opening input files" in str(e):
		print("ERROR. Postprocessing failed. Deleting file.")
		songdirectory = os.path.join(downloaddirectory, artist ,albumname)
		try:
			searchresults = [tiedosto for tiedosto in os.listdir(songdirectory) if songname in tiedosto]
		except FileNotFoundError:
			print("Virhe: Annettua kansiota ei löytynyt.")

		poistettava =  os.path.join(songdirectory, str(searchresults))
		filter1 = "'[]"
		for char in filter1:
			poistettava = poistettava.replace(char, "")

		if os.path.isfile(poistettava):
			os.remove(poistettava)
		else:
			if diagnosis == 1:
				print("Poistettava file path: " + poistettava)
			print("Could not delete corrupted file automatically. Trying backup deletion. ")
			poistettava2 =  os.path.join(songdirectory, songname + ".webm")
			filter2 = '?ü"[];:,()®*\''
			for char in filter2:
				poistettava2 = poistettava2.replace(char, "")
			if os.path.isfile(poistettava2):
				print("Deleting file: " + poistettava2)
				os.remove(poistettava2)
			else:
				print("File deleting backup method did not work.")
				print("Tried to delete file: " + poistettava2)
		addlogentry(f"Post processing error: {getstructure(artist, albumname, songname, fileformat)}")

	elif "--max-downloads" in str(e):
			if diagnosis == 1:
				print("Max downloads reached")
	else:
		addlogentry(f"Failed to download: {getstructure(artist, albumname, songname, fileformat)} Error occured: {e}, keyword: {filteredsongline}")

def getvideoid(songname, artist, threadnumber):
	if diagnosis == 1:
		print("Trying to get video ID.")
	hakusana = str(songname +" " + artist)
	yt = ytmusicapi.YTMusic()
	if diagnosis == 1:
		print("YT Music Keyword: " + str(hakusana)+ " on thread " + str(threadnumber))

	tulokset = yt.search(hakusana, filter="songs")

	videoid = None
	for r in tulokset:
		if r.get("resultType") == "song" and r.get("album") and r["album"].get("name"):
			videoid = r["videoId"]
			break

	if diagnosis == 1:
		print("Video ID: " + str(videoid) + " on thread " + str(threadnumber))
	if diagnosis == 1 and videoid:
		print("Video ID was successfully acquired.")
	return videoid

def downloadyt(songname, artist, albumname, threadnumber):
	if diagnosis == 1:
		print("Trying to download from Youtube")
	hakusana = str(songname + artist)
	albumname, songname, artist, songfilewithoutformat, filteredsongline, rating = getsonginfo(threadnumber)
	ytoptions = setytoptions(threadnumber)
	if diagnosis == 1:
		print("YouTube keyword: " + str(hakusana))
		print("YouTube options: " + str(ytoptions))
	with YoutubeDL(ytoptions) as ydl:
		try:
			c = ydl.download(f"ytsearch:{hakusana}")
			if diagnosis == 1:
				print("YT return code: " + str(c))

		except Exception as e:
			yterror(e, artist, albumname, songname, threadnumber)

def downloadytmusic(threadnumber, songname, artist, albumname, videoid):
	albumname, songname, artist, songfilewithoutformat, filteredsongline, rating = getsonginfo(threadnumber)
	ytoptions = setytoptions(threadnumber)
	if diagnosis == 1:
		print("Trying to download from YTMusic")
		print("Options: " + str(ytoptions))
	try:
		if videoid:
			if not "ERROR" in str(videoid):
				with YoutubeDL(ytoptions) as ydl:
					try:
						c = ydl.download(f"https://music.youtube.com/watch?v={videoid}")
						if diagnosis == 1:
							print("YTMusic return code: " + str(c))
					except Exception as e:
						yterror(e, artist, albumname, songname, threadnumber)
			else:
				addlogentry("ERROR. Failed to download from YTMusic. Downloading from youtube. ERROR in videoID. On thread "+ str(threadnumber))
				if diagnosis == 1:
					print("ERROR. Failed to download from YTMusic. Downloading from youtube. ERROR in videoID. On thread "+ str(threadnumber))
				downloadyt(songname, artist, albumname, threadnumber)
		else:
			addlogentry("ERROR. Failed to download from YTMusic. Downloading from youtube. No videoID was recieved. On thread "+ str(threadnumber))
			if diagnosis == 1:
				print("ERROR. Failed to download from YTMusic. Downloading from youtube. No videoID was recieved. On thread "+ str(threadnumber))
			downloadyt(songname, artist, albumname, threadnumber)
	except Exception as e:
		if diagnosis == 1:
			print("ERROR. Failed to download from YTMusic. Downloading from youtube. Exception: " + e)
		addlogentry("ERROR. Failed to download from YTMusic. Downloading from youtube. Exception: " + e)
		yterror(e, artist, albumname, songname, threadnumber)
		downloadyt(songname, artist, albumname, threadnumber)

def getmetadata(threadnumber, songname, artist):
	print (f"Trying to get albumname. Artist {artist}, Song {songname}")
	# Search for the artist
	search_url = f"https://musicbrainz.org/ws/2/recording?query=artist:{artist} AND recording:{songname}&fmt=json"
	response = requests.get(search_url)

	if response.status_code == 200:
		data = response.json()
		if data['recordings']:
			# Get the first recording found
			recording = data['recordings'][0]
			# Get the release information
			release_id = recording['releases'][0]['id']
			release_url = f"https://musicbrainz.org/ws/2/release/{release_id}?fmt=json"
			release_response = requests.get(release_url)

			if release_response.status_code == 200:
				release_data = release_response.json()
				albumname = release_data['title']
				return str(albumname)

			else:
				print( "Error fetching release data.")
				return ("")
		else:
			print( "No recordings found.")
			time.sleep(5)
			return ("")
	else:
		return ("")

def getmoremetadata(threadnumber, songname, artist):
	try:
		albumname =""
		albumname = getmetadata(threadnumber, songname, artist)

		if Settings["SMLD-retry"]:
			if albumname == "":
				print("Rate limit reached. Retrying in 12 seconds...----------------------------------------------------------------")
				time.sleep(12)
				getmetadata(threadnumber, songname, artist)

	except Exception:
		albumname = ("")

	if diagnosis == 1:
		print(f"The album for '{songname}' by '{artist}' is: {albumname}")
	return albumname

def updatemetadata(artist, albumname, songname, threadnumber):
	if diagnosis == 1:
		print("m4a detected")
	try:
		# Lataa M4A-tiedosto
		tiedosto = os.path.join(downloaddirectory, getstructure(artist, albumname, songname, fileformat))
		# for char in filter:
		# 	tiedosto = str(tiedosto.replace(char, ""))
		# tiedosto = str(tiedosto + "." + fileformat)
		if diagnosis == 1:
			print("Tiedosto on: " + tiedosto +" on thread" + str(threadnumber))

		if not os.path.isfile(tiedosto):
			print(f"ERROR. File {tiedosto} was not found when adding metadata.")
		if albumname == "":
			print("ERROR albumname is empty on thread " + str(threadnumber))
		if artist == "":
			print("ERROR artist name is empty on thread " + str(threadnumber))
		audio = MP4(tiedosto)
		try:
			# Lisää metatiedot
			if not albumname == "":
				audio["\xa9alb"] = albumname  # Albumin nimi
			audio["\xa9ART"] = artist  # Artistin nimi
			audio["aART"] = artist
			audio["\xa9nam"] = songname

			#‘\xa9day’ – year
			#‘\xa9gen’ – genre
		except Exception as e:
			print(f"Error in updating metadata e211: {e}")
		try:
			# Tallenna muutokset
			audio.save()
		except Exception as e:
			print(f"Error in updating metadata e212: {e}")
		if diagnosis == 1:
			print("Metadata added to file: " + str(tiedosto))
			print(f"Metadata: artist: {artist} album: {albumname}")
	except Exception as e:
		print(f"Error in updating metadata e2: {e}")
		if "only a top-level atom can have zero length" in str(e):
			addlogentry("File " + tiedosto + " might be currpted for an unknown reason.")
			print("File corrupted")
			os.remove(tiedosto)
			print("Corrupted file deleted.")
			downloadyt(songname, artist, albumname, threadnumber)

		elif "not a MP4 file" in str(e):
			print("File download not finished")
			addlogentry("File " + tiedosto + " download was not finished for an unknown reason.")
			os.remove(tiedosto)
			print("Corrupted file deleted.")
			downloadyt(songname, artist, albumname, threadnumber)

		else:
			addlogentry("Mutagen error: " + str(e) + " In thread " + str(threadnumber))
			addlogentry("With file: " + tiedosto+ " Artist " + artist + " Albumn " + albumname)

def setupSMLD(threadcount, libraryfilelocation):
	if diagnosis == 1:
		print("------------------------------------------------------------------SMLD STARTS-----------------------------------------------------------------")
	if os.path.isfile(libraryfilelocation):
		threadnumber = 0
		getinfo()
		emptyfails()
		createsonglist()
		dividesonglist()
		albumname, songname, artist, songfilewithoutformat, filteredsongline, rating  = getsonginfo(threadnumber)
		setupplaylists()
		if startrunloop_after_setup:
			SMLDpage.startthreads()
		def measurerate_a():
			SMLDprogressTracker.measurerate()
		measurerate_b = threading.Thread(target=measurerate_a)
		measurerate_b.start()
	else:
		print("ERROR. Given path is not a file. Path: " + libraryfilelocation)

def runsmld(threadnumber):
	global filenotfound
	try:
		while True:
			try:
				checkfails()
			except Exception:
				print("Fail checking failed")

			if diagnosis == 1:
				print("Thread " + str(threadnumber) +" is running.--------------------------------------------------------------------------------------------------------------------------------")

			if cancel:
				print("cancel")
				break

			if donelist[threadnumber]:
				print("done")
				break
			libraryfiledirectory = os.path.join(getBaseConfigDir(),"SMLD", "Temp", "Songlist" + str(threadnumber) + ".txt")
			with open(libraryfiledirectory, 'r', encoding='utf-8') as tiedosto:
				if diagnosis == 1:
					print("Rivit updated")
				rivit = tiedosto.readlines()
			if not rivit:  # Lopeta, jos tiedosto on tyhjä
				print("File is empty. No more files to add.")

				donelist[threadnumber] = True

			getinfo()
			if rivit:
				getsonginfo(threadnumber)
				albumname, songname, artist, songfilewithoutformat, filteredsongline, rating = getsonginfo(threadnumber)

			print(artist, songname, albumname)
			if diagnosis == 1:
				print("Checking if file exists before downloading. File: " + getstructure(artist, albumname, songname, fileformat))
			if not os.path.isfile(os.path.join(downloaddirectory, getstructure(artist, albumname, songname, fileformat))):
				if diagnosis == 1:
					print("File does not exist: " + getstructure(artist, albumname, songname, fileformat))
				addlogentry("File did not download correctly due to an error. File is: " + getstructure(artist, albumname, songname, fileformat))

				source = Settings["SMLD-source"]
				if source == "YouTube":
					downloadyt(songname, artist, albumname, threadnumber)
				elif source == "YouTube Music":
					videoid = getvideoid(songname, artist, threadnumber)
					metadatayt = Settings["SMLD-useytmetadata"]
					downloadytmusic(threadnumber, songname, artist, albumname, videoid)
					if metadatayt == True:
						if diagnosis:
							print("Using metadata from YT Music")
						if videoid:
							if not "ERROR" in str(videoid):
								albumname = getmoremetadata(threadnumber, songname, artist)
			else:
				if diagnosis == 1:
					print("File already exists, skipping download. " + os.path.join(downloaddirectory, getstructure(artist, albumname, songname, fileformat)))

			updatemetadata(artist, albumname, songname, threadnumber)
			if diagnosis == 1:
				print("Filtered song line: " + filteredsongline +" on thread " + str(threadnumber))

			if rivit:
				addtoplaylists(threadnumber)
			if os.path.isfile(os.path.join(downloaddirectory, getstructure(artist, albumname, songname, fileformat))):
				emptyfails()
				tiedostonimi = removeline(filteredsongline, threadnumber)
				if diagnosis == 1:
					print(f"File {getstructure(artist, albumname, songname, fileformat)} was saved")
				try:
					if diagnosis == 1:
						print("Adding entry to download log.")
					with open(os.path.expanduser("~/YTMediaTool/SMLD_History.txt"), 'a', encoding='utf-8') as history:
						history.write(f"File {getstructure(artist, albumname, songname, fileformat)} was saved at {datetime.now()}.")
						history.write("\n")

				except Exception:
					if diagnosis == 1:
						print("Log entry failed.-------------------------------")
			else:
				downloadfail()
				print("The file was not saved due to an unknown error.")
				addlogentry(f"File save error while trying to download: {getstructure(artist, albumname, songname, fileformat)} on thread {threadnumber}")
			SMLDprogressTracker.check_status()
			SMLDprogressTracker.trackprogress()

	except FileNotFoundError:

		filenotfound = True
		print(f"Tiedostoa '{tiedostonimi}' ei löydy.")
	except Exception as e:
		print(f"An unexpected error occured e12: {e}")
		addlogentry("Main loop error: " + str(e) + " on thread" + str(threadnumber))
		addlogentry(f"While trying to download: {downloaddirectory} {artist} {albumname} {songname} Thread: {threadnumber}")

