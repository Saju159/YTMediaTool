from tkinter import messagebox
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

diagnosis = 1 #1 = on, 0 = off
startrunloop_after_setup = True #default true, stop loop from running after setup when false
enable_yt_output = False #enable YT-DLP output printing

filter = '?ü"[];:,.()®*\'é' #global filter for song album and artist names

def clearlog():
	with open(os.path.join(getBaseConfigDir(),"SMLD","SMLDlog.txt"), 'w') as log:
		log.write("")
		log.close()
	if diagnosis == 1:
		print("Log cleared")

def getinfo():
	global libraryfiledirectory, libraryfiledirectory, downloaddirectory, fileformat
	with open(os.path.join(getBaseConfigDir(),"SMLD", "Temp", "downloaddirectory.txt")) as f:
		downloaddirectory = f.read()
		f.close()

	with open(os.path.join(getBaseConfigDir(),"SMLD", "Temp", "libraryfiledirectory.txt")) as f:
		libraryfiledirectory = f.read()
		f.close()

	with open(os.path.join(getBaseConfigDir(),"SMLD", "Temp", "fileformat.txt")) as f:
		fileformat= f.read()
		f.close()

	if diagnosis == 1:
		print(f"Download Directory: {downloaddirectory}")
		print(f"Library location: {libraryfiledirectory}")
		print("info acquired")

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
			filetype = str(libraryfiledirectory).find(".txt")
			with open(libraryfiledirectory, 'r', encoding='utf-8') as tiedosto:
				rivit2 = tiedosto.readlines()
			if not filetype == -1:
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
			else:
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
			if diagnosis == 1:
				print("File saved successfully.")
	except Exception as e:
		print(f"An error occured231: {e}")
		messagebox.showinfo("An error occured", e)
		with open(os.path.join(getBaseConfigDir(),"SMLD","SMLDlog.txt"), 'a', encoding='utf-8') as log:
			log.write("Error: " + str(e))
			log.write("\n")
			#log.write(f"While trying to download: {downloaddirectory} {artist} {albumname} {songname}")
			log.close()
	#Delete empty lines:
	with open(os.path.join(getBaseConfigDir(),"SMLD", "Temp", "Songlist.txt"), 'r', encoding='utf-8') as file:
		lineswithempty = file.readlines()
	non_empty_lines = [line for line in lineswithempty if line.strip()]
	with open(os.path.join(getBaseConfigDir(),"SMLD", "Temp", "Songlist.txt"), 'w', encoding='utf-8') as file:
		file.writelines(non_empty_lines)
		file.close()

def getsonginfo(threadnumber):
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
		if not filetype == -1:
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

				with open(os.path.join(getBaseConfigDir(),"SMLD", "Temp", "songinfo.txt"), "w") as f:
					f.write(artist + "\n "+ songname + "\n" + albumname)
					f.close()
		else:
			if diagnosis == 1:
				print("Spotify or iTunes lite.")
			csvparts = filteredsongline.split(',')
			songname = f"{csvparts[0]}"
			for char in filter:
				songname = songname.replace(char, "")
			artist = f"{csvparts[1]}"
			for char in filter:
				artist = artist.replace(char, "")
			albumname = f"{csvparts[2]}"
			for char in filter:
				albumname = albumname.replace(char, "")
			rating = ""  #set rating to none as csv does not contain rating data
			with open(os.path.join(getBaseConfigDir(),"SMLD", "Temp", "songinfo.txt"), "w") as f:
				f.write(artist + "\n "+ songname + "\n" + albumname)
				f.close()

	songfilewithoutformat = os.path.join(downloaddirectory, artist ,albumname, songname)
	for char in filter:
		songfilewithoutformat = songfilewithoutformat.replace(char, "")
	if diagnosis == 1:
		print("Lopullinen tiedosto on: " + songfilewithoutformat)

	return albumname, songname, artist, songfilewithoutformat, filteredsongline, rating

def addtoplaylists(threadnumber):
	albumname, songname, artist, songfilewithoutformat, filteredsongline, rating = getsonginfo(threadnumber)
	currentdownloadplaylist = (os.path.join(downloaddirectory, "CurrentDownload.m3u" ))
	favoritesplaylist = (os.path.join(downloaddirectory, "Favorites.m3u" ))
	with open(currentdownloadplaylist, 'a', encoding='utf-8') as playlist:
		playlist.write(artist +"/" +  albumname + "/" + songname + "." + fileformat)
		playlist.write("\n")
		playlist.close()
		if diagnosis == 1:
			print("Current download playlist written")

	if rating == "2":
		with open(favoritesplaylist, 'a', encoding='utf-8') as playlist:
			playlist.write(artist +"/" +  albumname + "/" + songname + "." + fileformat)
			playlist.write("\n")
			playlist.close()

def setupplaylists(songfilewithoutformat):
	global currentdownloadplaylist, favoritesplaylist
	currentdownloadplaylist = (os.path.join(downloaddirectory, "CurrentDownload.m3u" ))
	with open(currentdownloadplaylist, 'w', encoding='utf-8') as f2:
		f2.write("#EXTM3U")
		f2.write("\n")
		f2.close()
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
		print("Download location: " + songfilewithoutformat + "." + fileformat)
	ytoptions = {
	'format': 'bestaudio',
	'max_downloads': 1,
	#'outtmpl': {'default': songfilewithoutformat + ".%(ext)s"},
	'outtmpl': {'default': songfilewithoutformat + "." + fileformat},
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
		with open(os.path.join(getBaseConfigDir(),"SMLD","SMLDlog.txt"), 'a', encoding='utf-8') as log:
			log.write(f"Failed to download: {songfilewithoutformat}.{fileformat} Video is age-restricted. Enabling browser cookies in the settings might help.")
			log.write("\n")
			log.close()

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

		with open(os.path.join(getBaseConfigDir(),"SMLD","SMLDlog.txt"), 'a', encoding='utf-8') as log:
			log.write(f"Post processing error: {songfilewithoutformat}.{fileformat}")
			log.write("\n")
			log.close()

	elif "--max-downloads" in str(e):
			if diagnosis == 1:
				print("Max downloads reached")
	else:
		with open(os.path.join(getBaseConfigDir(),"SMLD","SMLDlog.txt"), 'a', encoding='utf-8') as log:
			log.write(f"Failed to download: {songfilewithoutformat}.{fileformat} Error occured: {e}, keyword: {filteredsongline}")
			log.write("\n")
			log.close()

def getvideoid(songname, artist, threadnumber):
	if diagnosis == 1:
		print("Trying to get video ID.")
	hakusana = str(songname +" " + artist)
	yt = ytmusicapi.YTMusic()
	if diagnosis == 1:
		print("YT Music Keyword: " + str(hakusana)+ " on thread " + str(threadnumber))
	videoid = yt.search(hakusana, filter="videos")[0]["videoId"]
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
				if diagnosis == 1:
					print("ERROR. Failed to download from YTMusic. Downloading from youtube. ERROR in videoID. On thread "+ str(threadnumber))
				downloadyt(songname, artist, albumname, threadnumber)
		else:
			if diagnosis == 1:
				print("ERROR. Failed to download from YTMusic. Downloading from youtube. No videoID was recieved. On thread "+ str(threadnumber))
			downloadyt(songname, artist, albumname, threadnumber)
	except Exception as e:
		if diagnosis == 1:
			print("ERROR. Failed to download from YTMusic. Downloading from youtube. Exception: " + e)
			yterror(e, artist, albumname, songname, threadnumber)
			downloadyt(songname, artist, albumname, threadnumber)

#def getytmetadata(videoid)


def updatemetadata(artist, albumname, songname, threadnumber):
	if diagnosis == 1:
		print("m4a detected")
	try:
		# Lataa M4A-tiedosto
		tiedosto = os.path.join(downloaddirectory, artist ,albumname, songname)
		for char in filter:
			tiedosto = str(tiedosto.replace(char, ""))
		tiedosto = str(tiedosto + "." + fileformat)
		if diagnosis == 1:
			print("Tiedosto on: " + tiedosto +" on thread" + str(threadnumber))

		if not os.path.isfile(tiedosto):
			print(f"ERROR. File {tiedosto} . {fileformat} was not found when adding metadata.")
		if albumname == "":
			print("ERROR albumname is empty on thread " + str(threadnumber))
		if artist == "":
			print("ERROR artist name is empty on thread " + str(threadnumber))
		audio = MP4(tiedosto)
		try:
			# Lisää metatiedot
			audio["\xa9alb"] = albumname  # Albumin nimi
			audio["\xa9ART"] = artist  # Artistin nimi
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
			with open(os.path.join(getBaseConfigDir(),"SMLD","SMLDlog.txt"), 'a', encoding='utf-8') as log:
				log.write("File " + tiedosto + " might be currpted for an unknown reason.")
				log.write("\n")
				log.close()
			print("File corrupted")
			os.remove(tiedosto)
			print("Corrupted file deleted.")
			downloadyt(songname, artist, albumname, threadnumber)

		elif "not a MP4 file" in str(e):
			print("File download not finished")
			with open(os.path.join(getBaseConfigDir(),"SMLD","SMLDlog.txt"), 'a', encoding='utf-8') as log:
				log.write("File " + tiedosto + " download was not finished for an unknown reason.")
				log.write("\n")
				log.close()
			os.remove(tiedosto)
			print("Corrupted file deleted.")
			downloadyt(songname, artist, albumname, threadnumber)

		else:
			with open(os.path.join(getBaseConfigDir(),"SMLD","SMLDlog.txt"), 'a', encoding='utf-8') as log:
				log.write("Mutagen error: " + str(e) + " In thread " + str(threadnumber))
				log.write("\n")
				log.write("With file: " + tiedosto+ " Artist " + artist + " Albumn " + albumname)
				log.write("\n")
				log.close()

def setupSMLD(threadcount, libraryfilelocation):
	if diagnosis == 1:
		print("------------------------------------------------------------------SMLD STARTS-----------------------------------------------------------------")
	clearlog()
	with open(os.path.join(getBaseConfigDir(),"SMLD", "Temp", "rate.txt"), "w") as f:
		f.write("0")
		f.close()
	if os.path.isfile(libraryfilelocation):
		threadnumber = 0
		getinfo()
		createsonglist()
		dividesonglist()
		albumname, songname, artist, songfilewithoutformat, filteredsongline, rating  = getsonginfo(threadnumber)
		setupplaylists(songfilewithoutformat)
		#tiedostonimi = os.path.join(getBaseConfigDir(),"SMLD", "Temp", "Songlist0.txt")
		if startrunloop_after_setup:
			SMLDpage.startthreads()
		# def measurerate_a():
		# 	SMLDprogressTracker.measurerate()
		# measurerate_b = threading.Thread(target=measurerate_a)
		# measurerate_b.start()
	else:
		print("ERROR. Given path is not a file. Path: " + libraryfilelocation)

def runsmld(threadnumber):
	try:
		while True:
			if diagnosis == 1:
				print("Thread " + str(threadnumber) +" is running.--------------------------------------------------------------------------------------------------------------------------------")
			with open(os.path.join(getBaseConfigDir(),"SMLD", "Temp", "cancel.txt"), "r") as f:
				cancel = f.read()
				f.close()
			if int(cancel) == 1:
				print("cancel")
				break

			with open(os.path.join(getBaseConfigDir(),"SMLD", "Temp", "Done" + str(threadnumber) + ".txt"), "r") as f:
				done = f.read()
				f.close()

			if int(done) == 1:
				print("done")
				break
			libraryfiledirectory = os.path.join(getBaseConfigDir(),"SMLD", "Temp", "Songlist" + str(threadnumber) + ".txt")
			with open(libraryfiledirectory, 'r', encoding='utf-8') as tiedosto:
				if diagnosis == 1:
					print("Rivit updated")
				rivit = tiedosto.readlines()
				#print("ensim. rivi:" + rivit[0].strip())
			if not rivit:  # Lopeta, jos tiedosto on tyhjä
				print("File is empty. No more files to add.")
				with open(os.path.join(getBaseConfigDir(),"SMLD", "Temp", "Done" + str(threadnumber) + ".txt"), 'w') as f:
					f.write("1")
			getinfo()
			if rivit:
				getsonginfo(threadnumber)
				albumname, songname, artist, songfilewithoutformat, filteredsongline, rating = getsonginfo(threadnumber)

			print(artist, songname, albumname)
			if diagnosis == 1:
				print("Checking if file exists before downloading. File: " + songfilewithoutformat + "."+fileformat)
			if not os.path.isfile(songfilewithoutformat + "."+fileformat):
				if diagnosis == 1:
					print("File does not exist: " + songfilewithoutformat + "."+fileformat)
				source = Settings["SMLD-source"]
				if source == "YouTube":
					downloadyt(songname, artist, albumname, threadnumber)
				elif source == "YouTube Music":
					videoid = getvideoid(songname, artist, threadnumber)
					downloadytmusic(threadnumber, songname, artist, albumname, videoid)
				else:
					if diagnosis == 1:
						print("Donwload source setting is invalid. source: " + source)
			else:
				if diagnosis == 1:
					print("File already exists, skipping download. " + songfilewithoutformat + "."+fileformat)
			if diagnosis == 1:
				print("Filtered song line: " + filteredsongline +" on thread " + str(threadnumber))
			#videoID =
			#getytmetadata(videoID)
			updatemetadata(artist, albumname, songname, threadnumber)
			if rivit:
				addtoplaylists(threadnumber)
			if os.path.isfile(songfilewithoutformat + "." + fileformat):
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
				if diagnosis == 1:
					print(f"File {songfilewithoutformat}.{fileformat} was saved")
			else:
				print("The file was not saved due to an unknown error.")
				with open(os.path.join(getBaseConfigDir(),"SMLD","SMLDlog.txt"), 'a', encoding='utf-8') as log:
					log.write(f"File save error while trying to download: {songfilewithoutformat}.{fileformat} on thread {threadnumber}")
					log.write("\n")
					log.close()
			SMLDprogressTracker.check_status()
			SMLDprogressTracker.trackprogress()

	except FileNotFoundError:
		messagebox.showinfo("File not found", f"File: '{tiedostonimi}' cannot be found.")
		print(f"Tiedostoa '{tiedostonimi}' ei löydy.")
	except Exception as e:
		print(f"An unexpected error occured e12: {e}")
		with open(os.path.join(getBaseConfigDir(),"SMLD","SMLDlog.txt"), 'a', encoding='utf-8') as log:
			log.write("Main loop error: " + str(e) + " on thread" + str(threadnumber))
			log.write("\n")
			try:
				log.write(f"While trying to download: {downloaddirectory} {artist} {albumname} {songname} Thread: {threadnumber}")
			except:
				print("Error while trying to write error log.")
			log.close()
