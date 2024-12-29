import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import subprocess
import os
from sys import platform
from mutagen.mp4 import MP4
import os.path
import time
from tkinter import filedialog as fd
import sys



polku3 = (os.getcwd())



with open(os.path.expanduser("~/YTMediaTool/Temp/downloaddirectory.txt")) as f:
    downloaddirectory = f.read()
    f.close()

with open(os.path.expanduser("~/YTMediaTool/Temp/libraryfiledirectory.txt")) as f:
    libraryfiledirectory = f.read()
    f.close()


print(f"Download Directory: {downloaddirectory}")
print(f"Library Directory: {libraryfiledirectory}")


playlistfile = (downloaddirectory + "Favorites.m3u")

with open(playlistfile, 'w', encoding='utf-8') as f2:
    f2.write("#EXTM3U")
    f2.write("\n")
    f2.close()

try:
    with open(libraryfiledirectory, 'r', encoding='utf-8') as tiedosto:
        rivit = tiedosto.readlines()

    with open((os.path.expanduser("~/YTMediaTool/Temp/Songlist.txt")), 'w', encoding='utf-8') as tiedosto:
        for rivi in rivit:
            osat = rivi.split('\t')  # Käytetään kahta tabulaattoria erottimena
            if len(osat) > 4:  # Tarkistetaan, että riittävästi osia löytyy
                uusi_rivi = f"{osat[0]}\t{osat[3]}\t{osat[4]}\t{osat[5]}\t{osat[6]}\n"  # Ensimmäinen ja kolmas osa
                tiedosto.write(uusi_rivi)

    print("File saved successfully.")
except Exception as e:
    print(f"An error occured: {e}")
    messagebox.showinfo("An error occured", e)


#Poistetaan tyhjät rivit:

with open(os.path.expanduser("~/YTMediaTool/Temp/Songlist.txt"), 'r', encoding='utf-8') as file:
    lines = file.readlines()
non_empty_lines = [line for line in lines if line.strip()]
with open(os.path.expanduser("~/YTMediaTool/Temp/Songlist.txt"), 'w', encoding='utf-8') as file:
    file.writelines(non_empty_lines)
    file.close()


def suorita_sudo_komennot_tiedostosta(tiedostonimi):
    try:
        while True:

            with open(os.path.expanduser("~/YTMediaTool/Temp/cancel.txt"), "r") as f:
                cancel = f.read()
                #print(cancel)
                if int(cancel) == 1:
                    print("cancel")
                    break
                f.close()

            # Luetaan tiedoston ensimmäinen rivi
            with open(tiedostonimi, 'r', encoding='utf-8') as tiedosto:
                rivit = tiedosto.readlines()

            if not rivit:  # Lopeta, jos tiedosto on tyhjä
                print("File is empty. No more files to add.")
                messagebox.showinfo("Done", "Downloading has been completed")
                break

            # Ota ensimmäinen rivi ja poista se tiedoston riveistä
            komento = rivit[0].strip()  # Poista rivin ympäriltä tyhjät merkit
            jäljellä_olevat_rivit = rivit[1:]  # Jäljellä olevat rivit


            filter = "/?ü"
            for char in filter:
                komento = komento.replace(char, "")

            komento2 = komento.replace(" ", "")

            osat = komento2.split('\t')
            if len(osat) > 2:
                songname = f"{osat[0]}"
                artist = f"{osat[1]}"
                albumname2 = f"{osat[2]}"
                albumname1 = albumname2.replace(")", "")
                albumname = albumname1.replace("(", "")
                genre = f"{osat[3]}"
                rate = f"{osat[4]}"


                print("----------------------------------------")
                print("Downloading:")

                print("Artist: " + str(artist))
                print("Song: " + str(songname))
                print("Albumname: " + str(albumname))
                #if favorited == "2":
                # print("This song is in your favorites.")

            if not komento:  # Ohitetaan tyhjät rivit
                # Päivitetään tiedosto ilman ensimmäistä riviä
                with open(tiedostonimi, 'w', encoding='utf-8') as tiedosto:
                    tiedosto.writelines(jäljellä_olevat_rivit)
                continue


            if not os.path.isfile(downloaddirectory + artist +"/" +  albumname + "/" + songname + ".m4a"):
                # Muodostetaan yt-dlp-komento
                sudo_komento = [
                    "yt-dlp",
                    "-f", "ba[ext=m4a]",
                    "-o", f"{downloaddirectory}{artist}/{albumname}/{songname}.m4a",
                    f"ytsearch:{komento}",
                    "--max-downloads", "1"
                ]

                #print (sudo_komento)
                try:

                    start = time.process_time()

                    # Suoritetaan komento
                    prosessi = subprocess.run(
                        sudo_komento, check=True, text=True,
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=os.environ
                    )

                    print(f"Downloading took: {time.process_time() - start}")

                    # Poistetaan ensimmäinen rivi tiedostosta
                    with open(tiedostonimi, 'w', encoding='utf-8') as tiedosto:
                        tiedosto.writelines(jäljellä_olevat_rivit)
                        continue

                except subprocess.CalledProcessError as e:
                    with open(tiedostonimi, 'w', encoding='utf-8') as tiedosto:
                        tiedosto.writelines(jäljellä_olevat_rivit)

                #print(downloaddirectory)
                if os.path.isfile(downloaddirectory + artist +"/" +  albumname + "/" + songname + ".m4a"):
                    print("Files saved")
                else:
                    print("The file was not saved due to an unknown error. The video might be age restricted.")

                    with open(os.path.expanduser("~/YTMediaTool/SMLDLog.txt"), 'a', encoding='utf-8') as log:
                        log.write(downloaddirectory + artist +"/" +  albumname + "/" + songname + ".m4a  " + "Was not saved as it should have been. The video might be age restricted.")
                        log.write("\n")
                        log.close()


                tiedosto = downloaddirectory + artist +"/" +  albumname + "/" + songname + ".m4a"
            else:

                print ("This file is already in your library.")

                # Poistetaan ensimmäinen rivi tiedostosta
                with open(tiedostonimi, 'w', encoding='utf-8') as tiedosto:
                    tiedosto.writelines(jäljellä_olevat_rivit)

                tiedosto = downloaddirectory + artist +"/" +  albumname + "/" + songname + ".m4a"

            if rate == "2":
                with open(playlistfile, 'a', encoding='utf-8') as playlist:
                    playlist.write(artist +"/" +  albumname + "/" + songname + ".m4a")
                    playlist.write("\n")
                    playlist.close()
    #Metadata:
            try:
                # Lataa M4A-tiedosto
                audio = MP4(tiedosto)

                # Lisää metatiedot
                audio["\xa9alb"] = albumname  # Albumin nimi
                audio["\xa9ART"] = artist  # Artistin nimi
                audio["\xa9gen"] = genre

                # Tallenna muutokset
                audio.save()

                print(f"Metadata added to file: " + downloaddirectory  + artist +"/" +  albumname + "/" + songname + ".m4a")
            except Exception as e:
                print(f"Error in updating metadata e2: {e}")
                with open(os.path.expanduser("~/YTMediaTool/SMLDLog.txt"), 'a', encoding='utf-8') as log:
                    log.write(str(e))
                    log.write("\n")
                    log.close()


    except FileNotFoundError:
        messagebox.showinfo("File not found", f"File: '{tiedostonimi}' cannot be found.")
        #print(f"Tiedostoa '{tiedostonimi}' ei löydy.")
    except Exception as e:
        print(f"An unexpected error occured e1: {e}")
        with open(os.path.expanduser("~/YTMediaTool/SMLDLog.txt"), 'a', encoding='utf-8') as log:
            log.write("Error: " + str(e))
            log.write("\n")
            log.write("While trying to run command: {sudo_komento}")
            log.close()

        print(sudo_komento)

# Käyttö
tiedostonimi = os.path.expanduser("~/YTMediaTool/Temp/Songlist.txt")  # Tekstitiedosto, joka sisältää hakusanat
suorita_sudo_komennot_tiedostosta(tiedostonimi)
