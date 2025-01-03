from tkinter import messagebox
import subprocess
import os
from mutagen.mp4 import MP4
import os.path
import time
from yt_dlp import YoutubeDL
from Settings import Settings


def setupSMLD():
    global polku3
    polku3 = (os.getcwd())


    with open(os.path.expanduser("~/YTMediaTool/Temp/downloaddirectory.txt")) as f:
        global downloaddirectory
        downloaddirectory = f.read()
        f.close()

    with open(os.path.expanduser("~/YTMediaTool/Temp/libraryfiledirectory.txt")) as f:
        libraryfiledirectory = f.read()
        f.close()

    with open(os.path.expanduser("~/YTMediaTool/Temp/fileformat.txt")) as f:
        global fileformat
        fileformat= f.read()
        f.close()


    print(f"Download Directory: {downloaddirectory}")
    print(f"Library Directory: {libraryfiledirectory}")

    global playlistfile
    playlistfile = (downloaddirectory + "Favorites.m3u")

    with open(playlistfile, 'w', encoding='utf-8') as f2:
        f2.write("#EXTM3U")
        f2.write("\n")
        f2.close()


    try:
        with open(libraryfiledirectory, 'r', encoding='utf-8') as tiedosto:
            ensimrivi = tiedosto.readlines(1)

            global filetype
            filetype = str(libraryfiledirectory).find(".txt")

            if not filetype == -1:
                print("Selected file is a iTunes media library. With .txt file format")

                with open(libraryfiledirectory, 'r', encoding='utf-8') as tiedosto:
                    rivit = tiedosto.readlines()

                with open((os.path.expanduser("~/YTMediaTool/Temp/Songlist.txt")), 'w', encoding='utf-8') as tiedosto:
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

                with open((os.path.expanduser("~/YTMediaTool/Temp/Songlist.txt")), 'w', encoding='utf-8') as tiedosto:
                    for rivi in rivit:
                        osat = rivi.split(',')
                        if len(osat) > 2:  # Tarkistetaan, että riittävästi osia löytyy
                            uusi_rivi = f"{osat[0]},{osat[1]},{osat[2]}\n"
                            tiedosto.write(uusi_rivi)


                delete = str(ensimrivi).find("Track name")

                if not delete == -1:
                    with open(os.path.expanduser("~/YTMediaTool/Temp/Songlist.txt"), 'r') as fin:
                        data = fin.read().splitlines(True)
                    with open(os.path.expanduser("~/YTMediaTool/Temp/Songlist.txt"), 'w') as fout:
                        fout.writelines(data[1:])
                    print("Header line removed")

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


def runsmld():
    global downloaddirectory, vaihtoehdot, fileformat, polku3, spotify, albumname, songname, artist

    with open(os.path.expanduser("~/YTMediaTool/Temp/downloaddirectory.txt")) as f:
        global downloaddirectory
        downloaddirectory = f.read()
        f.close()

    with open(os.path.expanduser("~/YTMediaTool/Temp/fileformat.txt")) as f:
        global fileformat
        fileformat= f.read()
        f.close()

    while True:
        time.sleep(0.05)
        with open(os.path.expanduser("~/YTMediaTool/Temp/cancel.txt"), "r") as f:
            cancel = f.read()
            f.close()
        if int(cancel) == 1:
            print("cancel")
            break

        f.close()
        tiedostonimi = os.path.expanduser("~/YTMediaTool/Temp/Songlist.txt")
        try:
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

            if not filetype == -1:
                print("Expanded iTunes format")
                osat = komento2.split('\t')
                if len(osat) > 2:
                    songname = f"{osat[0]}"
                    artist = f"{osat[1]}"
                    albumname2 = f"{osat[2]}"
                    albumname1 = albumname2.replace(")", "")
                    albumname = albumname1.replace("(", "")
                    genre = f"{osat[3]}"
                    rate = f"{osat[4]}"

                    with open(os.path.expanduser("~/YTMediaTool/Temp/songinfo.txt"), "w") as f:
                        f.write(artist + "\n "+ songname + "\n" + albumname)
                        f.close()
            else:
                print("Spotify or iTunes lite.")
                osat = komento2.split(',')
                songname = f"{osat[0]}"
                songname = songname.replace('"','')
                artist = f"{osat[1]}"
                artist = artist.replace('"','')
                albumname = f"{osat[2]}"
                albumname = albumname.replace('"','')
                genre = ""
                rate = ""

                with open(os.path.expanduser("~/YTMediaTool/Temp/songinfo.txt"), "w") as f:
                    f.write(artist + "\n "+ songname + "\n" + albumname)
                    f.close()

            print("----------------------------------------")
            print("Downloading:")

            print("Artist: " + str(artist))
            print("Song: " + str(songname))
            print("Albumname: " + str(albumname))


            if not komento:  # Ohitetaan tyhjät rivit
                # Päivitetään tiedosto ilman ensimmäistä riviä
                with open(tiedostonimi, 'w', encoding='utf-8') as tiedosto:
                    tiedosto.writelines(jäljellä_olevat_rivit)
                continue


            if not os.path.isfile(downloaddirectory + artist +"/" +  albumname + "/" + songname + ".m4a"):
                global vaihtoehdot
                vaihtoehdot = {
                'format': "ba",
                'max_downloads': 1,
                'outtmpl': {'default': f"{downloaddirectory}{artist}/{albumname}/{songname}.%(ext)s"},
                'final_ext' : fileformat,
                'postprocessors' : [{'key': 'FFmpegVideoConvertor', 'preferedformat': fileformat}]
                }

                if "FFmpeg_path" in Settings:
                    vaihtoehdot["ffmpeg_location"] = Settings["FFmpeg_path"]

                start = time.process_time()
                try:

                    with YoutubeDL(vaihtoehdot) as ydl:
                        try:
                            c = ydl.download(f"ytsearch:{komento}")
                            print("return code: " + str(c))

                        except Exception as e:
                            print(f"An unexpected error occured e3: {e}")

                    # Poistetaan ensimmäinen rivi tiedostosta
                    with open(tiedostonimi, 'w', encoding='utf-8') as tiedosto:
                        tiedosto.writelines(jäljellä_olevat_rivit)

                except subprocess.CalledProcessError as e:
                    print("Virhe: " + str(e))
                    with open(tiedostonimi, 'w', encoding='utf-8') as tiedosto:
                        tiedosto.writelines(jäljellä_olevat_rivit)

                print(f"Downloading took: {time.process_time() - start}")

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
                continue

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

                print("Metadata added to file: " + downloaddirectory  + artist +"/" +  albumname + "/" + songname + ".m4a")
            except Exception as e:
                print(f"Error in updating metadata e2: {e}")
                with open(os.path.expanduser("~/YTMediaTool/SMLDLog.txt"), 'a', encoding='utf-8') as log:
                    log.write(str(e))
                    log.write("\n")
                    log.close()


        except FileNotFoundError:
            messagebox.showinfo("File not found", f"File: '{tiedostonimi}' cannot be found.")
            #print(f"Tiedostoa '{tiedostonimi}' ei löydy.")
        # except Exception as e:
        #     print(f"An unexpected error occured e1: {e}")
        #     with open(os.path.expanduser("~/YTMediaTool/SMLDLog.txt"), 'a', encoding='utf-8') as log:
        #         log.write("Error: " + str(e))
        #         log.write("\n")
        #         log.write("While trying to run command: {sudo_komento}")
        #         log.close()


