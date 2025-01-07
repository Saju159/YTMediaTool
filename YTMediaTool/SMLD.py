from tkinter import messagebox
import subprocess
import os
from mutagen.mp4 import MP4
import os.path
import time
from yt_dlp import YoutubeDL
from Settings import Settings
from Common import getBaseConfigDir

if not os.path.isfile(os.path.join(getBaseConfigDir(),"SMLD","SMLDlog.txt")):
	with open(os.path.join(getBaseConfigDir(),"SMLD","SMLDlog.txt"), 'w') as log:
		log.close()

def setupSMLD():
	global polku3
	polku3 = (os.getcwd())


	with open(os.path.join(getBaseConfigDir(),"SMLD", "Temp", "downloaddirectory.txt")) as f:
		global downloaddirectory
		downloaddirectory = f.read()
		f.close()

	with open(os.path.join(getBaseConfigDir(),"SMLD", "Temp", "libraryfiledirectory.txt")) as f:
		libraryfiledirectory = f.read()
		f.close()

	with open(os.path.join(getBaseConfigDir(),"SMLD", "Temp", "fileformat.txt")) as f:
		global fileformat
		fileformat= f.read()
		f.close()


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
			filetype = str(libraryfiledirectory).find(".txt")

			if not filetype == -1:
				print("Selected file is a iTunes media library. With .txt file format")

				playlistfile = (os.path.join(downloaddirectory, "Favorites.m3u" ))

				with open(playlistfile, 'w', encoding='utf-8') as f2:
					f2.write("#EXTM3U")
					f2.write("\n")
					f2.close()

				with open(libraryfiledirectory, 'r', encoding='utf-8') as tiedosto:
					rivit = tiedosto.readlines()

				with open((os.path.join(getBaseConfigDir(),"SMLD", "Temp", "Songlist.txt")), 'w', encoding='utf-8') as tiedosto:
					for rivi in rivit:
						osat = rivi.split('\t')  # Käytetään kahta tabulaattoria erottimena
						if len(osat) > 4:  # Tarkistetaan, että riittävästi osia löytyy
							uusi_rivi = f"{osat[0]}\t{osat[3]}\t{osat[4]}\t{osat[5]}\t{osat[6]}\n"  # Ensimmäinen ja kolmas osa
							tiedosto.write(uusi_rivi)

				print("File saved successfully.")

			else:
				print("Selected file is a iTunes or Spotify media library.")


				with open(libraryfiledirectory, 'r', encoding='utf-8') as tiedosto:
					rivit = tiedosto.readlines()

				with open((os.path.join(getBaseConfigDir(),"SMLD", "Temp", "Songlist.txt")), 'w', encoding='utf-8') as tiedosto:
					for rivi in rivit:
						osat = rivi.split(',')
						if len(osat) > 2:  # Tarkistetaan, että riittävästi osia löytyy
							uusi_rivi = f"{osat[0]},{osat[1]},{osat[2]}\n"
							tiedosto.write(uusi_rivi)


				delete = str(ensimrivi).find("Track name")

				if not delete == -1:
					with open(os.path.join(getBaseConfigDir(),"SMLD", "Temp", "Songlist.txt"), 'r') as fin:
						data = fin.read().splitlines(True)
					with open(os.path.join(getBaseConfigDir(),"SMLD", "Temp", "Songlist.txt"), 'w') as fout:
						fout.writelines(data[1:])
					print("Header line removed")

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

	with open(os.path.join(getBaseConfigDir(),"SMLD", "Temp", "Songlist.txt"), 'r', encoding='utf-8') as file:
		lines = file.readlines()
	non_empty_lines = [line for line in lines if line.strip()]
	with open(os.path.join(getBaseConfigDir(),"SMLD", "Temp", "Songlist.txt"), 'w', encoding='utf-8') as file:
		file.writelines(non_empty_lines)
		file.close()


def runsmld():
	global downloaddirectory, vaihtoehdot, fileformat, polku3, filetype, albumname, songname, artist, playlistfile1

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

		f.close()
		tiedostonimi = os.path.join(getBaseConfigDir(),"SMLD", "Temp", "Songlist.txt")
		try:
			# Luetaan tiedoston ensimmäinen rivi
			with open(tiedostonimi, 'r', encoding='utf-8') as tiedosto:
				rivit = tiedosto.readlines()

			if not rivit:  # Lopeta, jos tiedosto on tyhjä
				print("File is empty. No more files to add.")
				with open(os.path.join(getBaseConfigDir(),"SMLD", "Temp", "Done.txt"), 'w') as f:
					f.write("1")
				messagebox.showinfo("Done", "Downloading has been completed")

				break

			# Ota ensimmäinen rivi ja poista se tiedoston riveistä
			komento = rivit[0].strip()  # Poista rivin ympäriltä tyhjät merkit
			jäljellä_olevat_rivit = rivit[1:]  # Jäljellä olevat rivit


			filter = "/?ü"
			for char in filter:
				komento = komento.replace(char, "")

			if not filetype == -1:
				#print("Expanded iTunes format")
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
				#print("Spotify or iTunes lite.")
				osat = komento.split(',')
				songname = f"{osat[0]}"
				songname = songname.replace('"','')
				artist = f"{osat[1]}"
				artist = artist.replace('"','')
				albumname = f"{osat[2]}"
				albumname = albumname.replace('"','')
				rate = ""

				with open(os.path.join(getBaseConfigDir(),"SMLD", "Temp", "songinfo.txt"), "w") as f:
					f.write(artist + "\n "+ songname + "\n" + albumname)
					f.close()

			if not komento:  # Ohitetaan tyhjät rivit
				# Päivitetään tiedosto ilman ensimmäistä riviä
				with open(tiedostonimi, 'w', encoding='utf-8') as tiedosto:
					tiedosto.writelines(jäljellä_olevat_rivit)
				continue

			lopullinentiedosto = os.path.join(downloaddirectory, artist ,albumname, songname)
			filter = '?ü"[];:,.()®*'
			for char in filter:
				lopullinentiedosto = lopullinentiedosto.replace(char, "")

			if not os.path.isfile(lopullinentiedosto + "."+fileformat):
				global vaihtoehdot
				vaihtoehdot = {
				'format': "ba",
				'max_downloads': 1,
				'outtmpl': {'default': lopullinentiedosto + ".%(ext)s"},
				'final_ext' : fileformat,
				'postprocessors' : [{'key': 'FFmpegVideoConvertor', 'preferedformat': fileformat}]
				}

				if "FFmpeg_path" in Settings:
					vaihtoehdot["ffmpeg_location"] = Settings["FFmpeg_path"]

				try:

					with YoutubeDL(vaihtoehdot) as ydl:
						try:
							c = ydl.download(f"ytsearch:{komento}")
							print("return code: " + str(c))

						except Exception as e:
							print(f"An unexpected error occured e3: {e}")

							if "Sign in to confirm your age." in str(e):
								with open(os.path.join(getBaseConfigDir(),"SMLD","SMLDlog.txt"), 'a', encoding='utf-8') as log:
									log.write(f"Failed to download: {lopullinentiedosto}.{fileformat} Video is age-restricted.")
									log.write("\n")
									log.close()
							else:
								if "--max-downloads" in str(e):
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
					#print("Files saved")
					continue
				else:

					print("The file was not saved due to an unknown error.")

				tiedosto = lopullinentiedosto + "." + fileformat
			else:

				# Poistetaan ensimmäinen rivi tiedostosta
				with open(tiedostonimi, 'w', encoding='utf-8') as tiedosto:
					tiedosto.writelines(jäljellä_olevat_rivit)
				continue

				tiedosto = lopullinentiedosto + "." + fileformat

			if not filetype == -1:
				if rate == "2":
					with open(playlistfile, 'a', encoding='utf-8') as playlist:
						playlist.write(artist +"/" +  albumname + "/" + songname + "." + fileformat)
						playlist.write("\n")
						playlist.close()


			with open(playlistfile1, 'a', encoding='utf-8') as playlist:
				playlist.write(artist +"/" +  albumname + "/" + songname + "." + fileformat)
				playlist.write("\n")
				playlist.close()

	#Metadata:
			if fileformat == "m4a":
				print("m4a detected")
				try:
					# Lataa M4A-tiedosto
					audio = MP4(tiedosto)

					# Lisää metatiedot
					audio["\xa9alb"] = albumname  # Albumin nimi
					audio["\xa9ART"] = artist  # Artistin nimi

					# Tallenna muutokset
					audio.save()

					print("Metadata added to file: " + downloaddirectory  + artist +"/" +  albumname + "/" + songname + "." + fileformat)
				except Exception as e:
					print(f"Error in updating metadata e2: {e}")
					with open(os.path.join(getBaseConfigDir(),"SMLD","SMLDlog.txt"), 'a', encoding='utf-8') as log:
						log.write("Mutagen error: " + str(e))
						log.write("\n")
						log.close()
			else:
				print("File is not a m4a. Skipping metadata.")

		except FileNotFoundError:
			messagebox.showinfo("File not found", f"File: '{tiedostonimi}' cannot be found.")
			#print(f"Tiedostoa '{tiedostonimi}' ei löydy.")
		except Exception as e:
			print(f"An unexpected error occured e1: {e}")
			with open(os.path.join(getBaseConfigDir(),"SMLD","SMLDlog.txt"), 'a', encoding='utf-8') as log:
				log.write("Main loop error: " + str(e))
				log.write("\n")
				log.write(f"While trying to download: {downloaddirectory} {artist} {albumname} {songname}")
				log.close()


