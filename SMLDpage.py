import tkinter as tk
from Common import openFilePicker
from tkinter import messagebox
import os
import os.path
from multiprocessing import Process
import time


global download
global downloaddirectory
#getprogress = None
global getprogress
process1 = None

librarydirectory, download = None, None
downloaddirectory1 = os.path.expanduser("~/YTMediaTool/Downloads/")

progress = 0

librarydirectory1 = " "

refresher = True

fileformats = {
    'm4a':	{'video': False, 'audio': True, 'ext': "m4a"},
    'mp3':	{'video': False, 'audio': True, 'ext': "mp3"},
    'ogg':	{'video': False, 'audio': True, 'ext': "ogg"},
    'flac':	{'video': False, 'audio': True, 'ext': "flac"},
}

with open(os.path.expanduser("~/YTMediaTool/Temp/cancel.txt"), "w") as f:
    f.write("0")
    f.close()

def createFrame(window):
    fileformat = tk.StringVar(value=next(iter(fileformats)))

    global frame
    frame = tk.Frame(window, width=600, height=380)
    frame.columnconfigure(2, weight=1)

    global showPage, hidePage
    def hidePage():
        frame.place_forget()
    def showPage():
        frame.place(y=34, h=-34, relwidth=1.0, relheight=1.0)

    librarydirectory = os.path.expanduser("~/YTMediaTool/")

    print (librarydirectory)

    def sellibdir():
        global librarydirectory
        picked_dir = openFilePicker(window, "openDir")
        if picked_dir:
            librarydirectory = picked_dir

        if not librarydirectory:
            librarydirectory = "~/YTMediaTool/Downloads/"

        lm = tk.Label(frame, text = "Nykyinen kirjastokansio: " + librarydirectory)
        lm.config(font =("Courier", 14))
        lm.place(x=5, y = 5)


    def seldownloaddir1():
        global downloaddirectory
        picked_dir = openFilePicker(window, "openDir")
        if picked_dir:
            downloaddirectory1 = picked_dir

        if not downloaddirectory1:
            downloaddirectory1 = os.path.expanduser("~/YTMediaTool/Downloads/")

    def sellibrarydirectory():
        global librarydirectory1
        #librarydirectory = filedialog.askdirectory(mustexist=True)
        librarydirectory1 = openFilePicker(window, "openFile")
        if librarydirectory1:
            print(librarydirectory1)
            librarydirectory.set(librarydirectory1)

        # Destination Directory
    tk.Label(frame, text="Destination directory: ").grid(row=1, column=1, sticky="W")

    downloaddirectory2 = tk.StringVar()
    downloaddirectory2.set(os.path.expanduser("~/YTMediaTool/Downloads/"))

    dirInputBox = tk.Entry(frame, textvariable=downloaddirectory2)
    dirInputBox.grid(row=1, column=2, sticky="WE")

    def seldir():
        picked_dir = openFilePicker(window, "openDir")
        if picked_dir:
            downloaddirectory2.set(picked_dir)

    selectDirButton = tk.Button(frame, text="Pick...", command=seldir)
    selectDirButton.grid(row=1, column=3)


    tk.Label(frame, text="Library list directory: ").grid(row=2, column=1, sticky="W")

    librarydirectory = tk.StringVar()
    librarydirectory.set("Enter library file directory here.")

    dirInputBox = tk.Entry(frame, textvariable=librarydirectory)
    dirInputBox.grid(row=2, column=2, sticky="WE")

    selectDirButton = tk.Button(frame, text="Pick...", command=sellibrarydirectory)
    selectDirButton.grid(row=2, column=3)

    downloaddirectory = downloaddirectory1

    info = tk.Label(frame, text="\n SMLD is a tool designed to download large amounts of audio files from YouTube. Currently it works straight out of the box with iTunes library lists that you can get by CTRL + A and CTRL + C from the iTunes application. Put that in a text file and select it with the library list selector. Lists for other music services are coming soon " + u"\u2122", wraplength = 500 )
    info.grid(row=8, column=1, columnspan = 3)

    fileformatDropdown = tk.OptionMenu(frame, fileformat, *fileformats)
    fileformatDropdown.grid(row=3, column=1, sticky="W")



    def refresher():
        with open(os.path.expanduser("~/YTMediaTool/Temp/cancel.txt"), "r") as f:
            cancel = f.read()
            if int(cancel) == 0:
                window.after(5000, refresher)

            else:
                print("cancel")

            f.close()


        with open(os.path.expanduser("~/YTMediaTool/Temp/songinfo.txt"), "r") as f:
            filter = "[]'"
            artist = f.readlines(1)
            for char in filter:
                artist = str(artist).replace(char, "")
                artist = artist.replace("\\n", "")
            songinfo1.config(text="Artist: "+ str(artist))
            song = f.readlines(2)
            for char in filter:
                song = str(song).replace(char, "")
                song = song.replace("\\n", "")
            songinfo2.config(text="Song: "+ str(song))
            album = f.readlines(3)
            for char in filter:
                album = str(album).replace(char, "")
            songinfo3.config(text="Album: "+ str(album))

        f.close()

        with open(os.path.expanduser("~/YTMediaTool/Temp/progress.txt"), "r") as f:
            progress = str(f.readlines())

            progress = progress.replace("[", "")
            progress = progress.replace("]", "")
            progress = progress.replace("'", "")

            pg.config(text = "Progress: "+ str(progress) + "%")
            #print(progress)
            f.close()


    def runSMLD():
        global process1
        if os.path.isfile(librarydirectory1):
            cancelb.grid(row=1, column=2, sticky="W")
            pg.grid(row=1, column=3)
            with open(os.path.expanduser("~/YTMediaTool/Temp/downloaddirectory.txt"), "w") as f:
                f.write(downloaddirectory1)
                f.close()

            with open(os.path.expanduser("~/YTMediaTool/Temp/libraryfiledirectory.txt"), "w") as f:
                f.write(str(librarydirectory1))
                f.close()

            with open(os.path.expanduser("~/YTMediaTool/Temp/cancel.txt"), "w") as f:
                f.write("0")
                f.close()

            with open(os.path.expanduser("~/YTMediaTool/Temp/fileformat.txt"), "w") as f:
                f.write(fileformat.get())
                f.close()

            songinfo2.grid(row=6, column=1, columnspan = 3, sticky="W")
            songinfo1.grid(row=5, column=1, columnspan = 3, sticky="W")
            songinfo3.grid(row=7, column=1, columnspan = 3, sticky="W")

            os.system("python SMLDprogressTracker.py")

            def refresher_a():
                os.system('python SMLD.py')


            process1 = Process(target=refresher_a)
            process1.start()

            window.after(1, refresher)

        else:
            messagebox.showinfo("File not found", "File cannot be found or it doesn't exist. Please enter a valid file path.")

    #runSMLD = subprocess.run(['python', 'SMLD.py', arg1, arg2])
    frame1 = tk.Frame(frame)
    frame1.grid(row=4, column=1, sticky="WE", columnspan=4)    #sticky="W" = tasaus west (ilmansuunnat)  columnspan=2 = monta saraketta grid vie
    #frame1.columnconfigure(2, weight=1)  #venyttää ensin saraketta 2
    tk.Button(frame1, text="Download", command=runSMLD).grid(row=1, column=1, sticky="W")

    def cancel():
        with open(os.path.expanduser("~/YTMediaTool/Temp/cancel.txt"), "w") as f:
            f.write("1")
            f.close()

        cancelb.grid_forget()
        pg.grid_forget()
        songinfo1.grid_forget()
        songinfo2.grid_forget()
        songinfo3.grid_forget()

    cancelb=tk.Button(frame1, text="Cancel", command=cancel)#.grid(row=30, column=0, sticky="E")

   # def refresh():
    #    def refresher_b():
     #       os.system("python SMLDprogressTracker.py")
      #  Process(target=refresher_b).start()



    #tk.Button(frame1, text="Refresh progress", command=refresh).grid(row=1, column=4, sticky="E")

    pg = tk.Label(frame1, text="Progress: "+ str(progress) + "%")


    global songinfo1
    songinfo1 = tk.Label(frame, )

    songinfo2 = tk.Label(frame)

    songinfo3 = tk.Label(frame)







