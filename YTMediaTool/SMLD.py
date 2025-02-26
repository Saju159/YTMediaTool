from tkinter import messagebox
import subprocess
import os
from mutagen.mp4 import MP4
import os.path
import time
from yt_dlp import YoutubeDL
from Settings import Settings
from Common import getBaseConfigDir
import ytmusicapi

diagnosis = 0 #1 = on, 0 = off

filter = '?ü"[];:,.()®*\'' #global filter for song album and artist names

if not os.path.isfile(os.path.join(getBaseConfigDir(),"SMLD","SMLDlog.txt")):
	with open(os.path.join(getBaseConfigDir(),"SMLD","SMLDlog.txt"), 'w') as log:
		log.close()

def setupSMLD(threadnumber, threadcount):
	global polku3
	polku3 = (os.getcwd())


	with open(os.path.join(getBaseConfigDir(),"SMLD", "Temp", "downloaddirectory.txt")) as f:
		global downloaddirectory
		downloaddirectory = f.read()
		f.close()

	with open(os.path.join(getBaseConfigDir(),"SMLD", "Temp", "libraryfiledirectory.txt")) as f:
		libraryfiledirectory2 = f.read()
		f.close()


	libraryfiledirectory = os.path.join(getBaseConfigDir(),"SMLD", "Temp", "Songlist" + str(threadnumber) + ".txt")

	with open(os.path.join(getBaseConfigDir(),"SMLD", "Temp", "fileformat.txt")) as f:
		global fileformat
		fileformat= f.read()
		f.close()

	if diagnosis == 1:
		print(f"Download Directory: {downloaddirectory}")
		print(f"Library Directory: {libraryfiledirectory}")

	try:
		global playlistfile1, playlistfile
		playlistfile1 = (os.path.join(downloaddirectory, "CurrentDownload.m3u" ))

		with open(playlistfile1, 'w', encoding='utf-8') as f2:
			f2.write("#EXTM3U")
			f2.write("\n")
			f2.close()


		with open(libraryfiledirectory, 'r', encoding='utf-8') as tiedosto:
			ensimrivi = tiedosto.readlines(1)

			global filetype
			filetype = str(libraryfiledirectory2).find(".txt")

			if not filetype == -1:
				if diagnosis == 1:
					print("Selected file is a iTunes media library. With .txt file format")

				playlistfile = (os.path.join(downloaddirectory, "Favorites.m3u" ))

				with open(playlistfile, 'w', encoding='utf-8') as f2:
					f2.write("#EXTM3U")
					f2.write("\n")
					f2.close()

				with open(libraryfiledirectory, 'r', encoding='utf-8') as tiedosto:
					rivit = tiedosto.readlines()

				with open((os.path.join(getBaseConfigDir(),"SMLD", "Temp", "Songlist" + str(threadnumber) + ".txt")), 'w', encoding='utf-8') as tiedosto:
					for rivi in rivit:
						osat = rivi.split('\t')  # Käytetään kahta tabulaattoria erottimena
						if len(osat) > 4:  # Tarkistetaan, että riittävästi osia löytyy
							uusi_rivi = f"{osat[0]}\t{osat[3]}\t{osat[4]}\t{osat[5]}\t{osat[6]}\n"  # Ensimmäinen ja kolmas osa
							tiedosto.write(uusi_rivi)
				if diagnosis == 1:
					print("File saved successfully.")

			else:
				if diagnosis == 1:
					print("Selected file is a iTunes or Spotify media library.")

				with open(libraryfiledirectory, 'r', encoding='utf-8') as tiedosto:
					rivit = tiedosto.readlines()

				with open((os.path.join(getBaseConfigDir(),"SMLD", "Temp", "Songlist" + str(threadnumber) + ".txt")), 'w', encoding='utf-8') as tiedosto:
					for rivi in rivit:
						osat = rivi.split(',')
						if len(osat) > 2:  # Tarkistetaan, että riittävästi osia löytyy
							uusi_rivi = f"{osat[0]},{osat[1]},{osat[2]}\n"
							tiedosto.write(uusi_rivi)

				delete = str(ensimrivi).find("Track name")

				if not delete == -1:
					with open(os.path.join(getBaseConfigDir(),"SMLD", "Temp", "Songlist" + str(threadnumber) + ".txt"), 'r') as fin:
						data = fin.read().splitlines(True)
					with open(os.path.join(getBaseConfigDir(),"SMLD", "Temp", "Songlist" + str(threadnumber) + ".txt"), 'w') as fout:
						fout.writelines(data[1:])

					if diagnosis == 1:
						print("Header line removed")
			if diagnosis == 1:
				print("File saved successfully.")


	except Exception as e:
		print(f"An error occured: {e}")
		messagebox.showinfo("An error occured", e)
		with open(os.path.join(getBaseConfigDir(),"SMLD","SMLDlog.txt"), 'a', encoding='utf-8') as log:
			log.write("Error: " + str(e))
			log.write("\n")
			log.write(f"While trying to download: {downloaddirectory} {artist} {albumname} {songname}")
			log.close()

	#Poistetaan tyhjät rivit:

	with open(os.path.join(getBaseConfigDir(),"SMLD", "Temp", "Songlist" + str(threadnumber) + ".txt"), 'r', encoding='utf-8') as file:
		lines = file.readlines()
	non_empty_lines = [line for line in lines if line.strip()]
	with open(os.path.join(getBaseConfigDir(),"SMLD", "Temp", "Songlist" + str(threadnumber) + ".txt"), 'w', encoding='utf-8') as file:
		file.writelines(non_empty_lines)
		file.close()


def runsmld(threadnumber):
	global downloaddirectory, vaihtoehdot, fileformat, polku3, filetype, albumname, songname, artist, playlistfile1

	if diagnosis == 1:

		if diagnosis == 1:
			print("-------------------------------------------------Next file----------------------------------------------------------------------------")

	with open(os.path.join(getBaseConfigDir(),"SMLD", "Temp", "downloaddirectory.txt")) as f:
		global downloaddirectory
		downloaddirectory = f.read()
		f.close()

	with open(os.path.join(getBaseConfigDir(),"SMLD", "Temp", "fileformat.txt")) as f:
		global fileformat
		fileformat= f.read()
		f.close()

	while True:
		time.sleep(0.05)
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

		f.close()
		tiedostonimi = os.path.join(getBaseConfigDir(),"SMLD", "Temp", "Songlist" + str(threadnumber) + ".txt")
		if diagnosis == 1:
			if diagnosis == 1:
				print("Theadnumeber:"  + str(threadnumber))
			#print(f"While trying to download: {downloaddirectory} {artist} {albumname} {songname}")
		try:
			# Luetaan tiedoston ensimmäinen rivi
			with open(tiedostonimi, 'r', encoding='utf-8') as tiedosto:
				rivit = tiedosto.readlines()

			if not rivit:  # Lopeta, jos tiedosto on tyhjä
				print("File is empty. No more files to add.")
				with open(os.path.join(getBaseConfigDir(),"SMLD", "Temp", "Done" + str(threadnumber) + ".txt"), 'w') as f:
					f.write("1")
				break

			# Ota ensimmäinen rivi ja poista se tiedoston riveistä
			if not rivit == "":
				komento = rivit[0].strip()  # Poista rivin ympäriltä tyhjät merkit
				jäljellä_olevat_rivit = rivit[1:]  # Jäljellä olevat rivit

			else:
				print ("Thread" + threadnumber +"file is empty")

			filter1 = "/?ü()"
			for char in filter1:
				komento = komento.replace(char, "")

			if not rivit == "":
				if not filetype == -1:
					if diagnosis == 1:
						print("Expanded iTunes format")
					osat = komento.split('\t')
					if len(osat) > 2:
						songname = f"{osat[0]}"
						artist = f"{osat[1]}"
						albumname2 = f"{osat[2]}"
						albumname1 = albumname2.replace(")", "")
						albumname = albumname1.replace("(", "")
						rate = f"{osat[4]}"

						with open(os.path.join(getBaseConfigDir(),"SMLD", "Temp", "songinfo.txt"), "w") as f:
							f.write(artist + "\n "+ songname + "\n" + albumname)
							f.close()
				else:
					if diagnosis == 1:
						print("Spotify or iTunes lite.")
					osat = komento.split(',')
					songname = f"{osat[0]}"
					for char in filter:
						songname = songname.replace(char, "")
					artist = f"{osat[1]}"
					for char in filter:
						artist = artist.replace(char, "")
					albumname = f"{osat[2]}"
					for char in filter:
						albumname = albumname.replace(char, "")
					rate = ""

					with open(os.path.join(getBaseConfigDir(),"SMLD", "Temp", "songinfo.txt"), "w") as f:
						f.write(artist + "\n "+ songname + "\n" + albumname)
						f.close()

			lopullinentiedosto = os.path.join(downloaddirectory, artist ,albumname, songname)
			for char in filter:
				lopullinentiedosto = lopullinentiedosto.replace(char, "")

			if not os.path.isfile(lopullinentiedosto + "."+fileformat):
				global vaihtoehdot
				vaihtoehdot = {
				'format': 'bestaudio',
				'max_downloads': 1,
				'outtmpl': {'default': lopullinentiedosto + ".%(ext)s"},
				'final_ext' : fileformat,
				'postprocessors' : [{'key': 'FFmpegVideoConvertor', 'preferedformat': fileformat}],
				'quiet': True,
				'noprogress': True
				}

				if "FFmpeg_path" in Settings:
					vaihtoehdot["ffmpeg_location"] = Settings["FFmpeg_path"]

				if len(Settings["YDL-CookiesFilePath"]) > 2:
					print("Using cookie file!")
					vaihtoehdot["cookiefile"] = str(Settings["YDL-CookiesFilePath"])
				elif Settings["BasicPage-Cookies"]:
					browser_to_grab_from = (Settings["BasicPage-browser"])
					print(f"Grabbing cookies from {browser_to_grab_from}!")
					vaihtoehdot["cookiesfrombrowser"] = (browser_to_grab_from, None, None, None)

				try:

					hakusana = str(songname + artist)
					source = Settings["SMLD-source"]
					with YoutubeDL(vaihtoehdot) as ydl:
						if source == "YouTube":
							try:
								c = ydl.download(f"ytsearch:{hakusana}")
								if diagnosis == 1:
									print("return code: " + str(c))

							except Exception as e:
								print(f"An unexpected error occured e3: {e}")

								if "Sign in to confirm your age." in str(e):
									with open(os.path.join(getBaseConfigDir(),"SMLD","SMLDlog.txt"), 'a', encoding='utf-8') as log:
										log.write(f"Failed to download: {lopullinentiedosto}.{fileformat} Video is age-restricted. Enabling browser cookies in the settings might help.")
										log.write("\n")
										log.close()
								else:
									if "--max-downloads" in str(e):
										if diagnosis == 1:
											print("Max downloads reached")
									else:
										with open(os.path.join(getBaseConfigDir(),"SMLD","SMLDlog.txt"), 'a', encoding='utf-8') as log:
											log.write(f"Failed to download: {lopullinentiedosto}.{fileformat} Error occured: {e}")
											log.write("\n")
											log.close()

						if source == "YouTube Music":
							try:
								yt = ytmusicapi.YTMusic()
								videoid = yt.search(hakusana)[0]["videoId"]
								if not "ERROR" in videoid:
									try:
										c = ydl.download(f"https://music.youtube.com/watch?v={videoid}")
										if diagnosis == 1:
											print("return code: " + str(c))

									except Exception as e:
										print(f"An unexpected error occured e3: {e}")

										if "Sign in to confirm your age." in str(e):
											with open(os.path.join(getBaseConfigDir(),"SMLD","SMLDlog.txt"), 'a', encoding='utf-8') as log:
												log.write(f"Failed to download: {lopullinentiedosto}.{fileformat} Video is age-restricted. Enabling browser cookies in the settings might help.")
												log.write("\n")
												log.close()
										else:
											if "--max-downloads" in str(e):
												if diagnosis == 1:
													print("Max downloads reached")
											else:
												with open(os.path.join(getBaseConfigDir(),"SMLD","SMLDlog.txt"), 'a', encoding='utf-8') as log:
													log.write(f"Failed to download: {lopullinentiedosto}.{fileformat} Error occured: {e}, keyword: {komento}")
													log.write("\n")
													log.close()
								else:
									try:
										c = ydl.download(f"ytsearch:{hakusana}")
										if diagnosis == 1:
											print("return code: " + str(c))

									except Exception as e:
										print(f"An unexpected error occured e3: {e}")

										if "Sign in to confirm your age." in str(e):
											with open(os.path.join(getBaseConfigDir(),"SMLD","SMLDlog.txt"), 'a', encoding='utf-8') as log:
												log.write(f"Failed to download: {lopullinentiedosto}.{fileformat} Video is age-restricted. Enabling browser cookies in the settings might help.")
												log.write("\n")
												log.close()
										else:
											if "--max-downloads" in str(e):
												if diagnosis == 1:
													print("Max downloads reached")
											else:
												with open(os.path.join(getBaseConfigDir(),"SMLD","SMLDlog.txt"), 'a', encoding='utf-8') as log:
													log.write(f"Failed to download: {lopullinentiedosto}.{fileformat} Error occured: {e}")
													log.write("\n")
													log.close()

							except Exception as e:
								print("Downloading from YouTube Music failed. Downloading from YouTube. Error: "+ str(e))

								try:
									c = ydl.download(f"ytsearch:{hakusana}")
									if diagnosis == 1:
										print("return code: " + str(c))

								except Exception as e:
									print(f"An unexpected error occured e3: {e}")

									if "Sign in to confirm your age." in str(e):
										with open(os.path.join(getBaseConfigDir(),"SMLD","SMLDlog.txt"), 'a', encoding='utf-8') as log:
											log.write(f"Failed to download: {lopullinentiedosto}.{fileformat} Video is age-restricted. Enabling browser cookies in the settings might help.")
											log.write("\n")
											log.close()
									else:
										if "--max-downloads" in str(e):
											if diagnosis == 1:
												print("Max downloads reached")
										else:
											with open(os.path.join(getBaseConfigDir(),"SMLD","SMLDlog.txt"), 'a', encoding='utf-8') as log:
												log.write(f"Failed to download: {lopullinentiedosto}.{fileformat} Error occured: {e}")
												log.write("\n")
												log.close()


					# Poistetaan ensimmäinen rivi tiedostosta
					with open(tiedostonimi, 'w', encoding='utf-8') as tiedosto:
						tiedosto.writelines(jäljellä_olevat_rivit)

				except subprocess.CalledProcessError as e:
					print("Virhe: " + str(e))
					with open(tiedostonimi, 'w', encoding='utf-8') as tiedosto:
						tiedosto.writelines(jäljellä_olevat_rivit)


				if os.path.isfile(lopullinentiedosto + "." + fileformat):
					if diagnosis == 1:
						print(f"File {lopullinentiedosto}.{fileformat} was saved")
				else:

					print("The file was not saved due to an unknown error.")
					with open(os.path.join(getBaseConfigDir(),"SMLD","SMLDlog.txt"), 'a', encoding='utf-8') as log:
						log.write(f"File save error while trying to download: {lopullinentiedosto} on thread {threadnumber}")
						log.close()

				tiedosto = lopullinentiedosto + "." + fileformat
			else:

				# Poistetaan ensimmäinen rivi tiedostosta
				with open(tiedostonimi, 'w', encoding='utf-8') as tiedosto:
					tiedosto.writelines(jäljellä_olevat_rivit)

				tiedosto = lopullinentiedosto + "." + fileformat

			if not filetype == -1:
				if rate == "2":
					with open(playlistfile, 'a', encoding='utf-8') as playlist:
						playlist.write(artist +"/" +  albumname + "/" + songname + "." + fileformat)
						playlist.write("\n")
						playlist.close()
			if diagnosis == 1:
				print(artist +"/" +  albumname + "/" + songname + "." + fileformat)
			with open(playlistfile1, 'a', encoding='utf-8') as playlist:
				playlist.write(artist +"/" +  albumname + "/" + songname + "." + fileformat)
				playlist.write("\n")
				playlist.close()
				if diagnosis == 1:
					print("Current download playlist written")

	#Metadata:
			if fileformat == "m4a":
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

						try:
							c = ydl.download(f"ytsearch:{hakusana}")
							if diagnosis == 1:
								print("return code: " + str(c))

						except Exception as e:
							print(f"An unexpected error occured e3: {e}")

							if "Sign in to confirm your age." in str(e):
								with open(os.path.join(getBaseConfigDir(),"SMLD","SMLDlog.txt"), 'a', encoding='utf-8') as log:
									log.write(f"Failed to download: {lopullinentiedosto}.{fileformat} Video is age-restricted. Enabling browser cookies in the settings might help.")
									log.write("\n")
									log.close()
							else:
								if "--max-downloads" in str(e):
									if diagnosis == 1:
										print("Max downloads reached")
								else:
									with open(os.path.join(getBaseConfigDir(),"SMLD","SMLDlog.txt"), 'a', encoding='utf-8') as log:
										log.write(f"Failed to download: {lopullinentiedosto}.{fileformat} Error occured: {e}")
										log.write("\n")
										log.close()

					elif "not a MP4 file" in str(e):
						print("File download not finished")
						with open(os.path.join(getBaseConfigDir(),"SMLD","SMLDlog.txt"), 'a', encoding='utf-8') as log:
						 	log.write("File " + tiedosto + " download was not finished for an unknown reason.")
						 	log.write("\n")
						 	log.close()
						os.remove(tiedosto)
						print("Corrupted file deleted.")

						try:
							c = ydl.download(f"ytsearch:{hakusana}")
							if diagnosis == 1:
								print("return code: " + str(c))

						except Exception as e:
							print(f"An unexpected error occured e3: {e}")

							if "Sign in to confirm your age." in str(e):
								with open(os.path.join(getBaseConfigDir(),"SMLD","SMLDlog.txt"), 'a', encoding='utf-8') as log:
									log.write(f"Failed to download: {lopullinentiedosto}.{fileformat} Video is age-restricted. Enabling browser cookies in the settings might help.")
									log.write("\n")
									log.close()
							else:
								if "--max-downloads" in str(e):
									if diagnosis == 1:
										print("Max downloads reached")
								else:
									with open(os.path.join(getBaseConfigDir(),"SMLD","SMLDlog.txt"), 'a', encoding='utf-8') as log:
										log.write(f"Failed to download: {lopullinentiedosto}.{fileformat} Error occured: {e}")
										log.write("\n")
										log.close()
					else:
						with open(os.path.join(getBaseConfigDir(),"SMLD","SMLDlog.txt"), 'a', encoding='utf-8') as log:
							log.write("Mutagen error: " + str(e) + " In thread " + str(threadnumber))
							log.write("\n")
							log.write("With file: " + tiedosto+ " Artist " + artist + " Albumn " + albumname)
							log.write("\n")
							log.close()
			else:
				if diagnosis == 1:
					print("File is not a m4a. Skipping metadata.")

			if not komento:  # Ohitetaan tyhjät rivit
				# Päivitetään tiedosto ilman ensimmäistä riviä
				with open(tiedostonimi, 'w', encoding='utf-8') as tiedosto:
					tiedosto.writelines(jäljellä_olevat_rivit)

		except FileNotFoundError:
			messagebox.showinfo("File not found", f"File: '{tiedostonimi}' cannot be found.")
			#print(f"Tiedostoa '{tiedostonimi}' ei löydy.")
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


