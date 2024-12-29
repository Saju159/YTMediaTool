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
from multiprocessing import Process
import signal




global download
global downloaddirectory
#getprogress = None
global getprogress
process1 = None

librarydirectory, download = None, None
downloaddirectory1 = os.path.expanduser("~/YTMediaTool/Downloads/")



progress = 0

#librarydirectory1 = os.path.expanduser("~/YTMediaTool/Librarylist/Librarylist.txt")

librarydirectory1 = " "

with open(os.path.expanduser("~/YTMediaTool/Temp/cancel.txt"), "w") as f:
    f.write("0")
    f.close()

def createFrame(window):
    global frame
    frame = tk.Frame(window, width=600, height=380)
    frame.columnconfigure(2, weight=1)

    global showPage, hidePage
    def hidePage():
        frame.place_forget()
    def showPage():
        frame.place(y=34, h=-34, relwidth=1.0, relheight=1.0)


    l1, l2, seldownloaddir, sellibdir, input1 = None, None, None, None, None

    librarydirectory = os.path.expanduser("~/YTMediaTool/")

    print (librarydirectory)

    if not os.path.exists(librarydirectory + "Temp/"):
        os.makedirs(librarydirectory + "Temp/")

    if not os.path.exists(librarydirectory + "Librarylist/"):
        os.makedirs(librarydirectory + "Librarylist/")


   # input1 = tk.Text(frame, height = 1, width = 50)
    #input1.place(x=110, y=  60)




    def sellibdir():
        global librarydirectory
        global windowp
        windowp = tk.Toplevel(window)
        windowp.withdraw()
        picked_dir = filedialog.askdirectory()
        if isinstance(picked_dir, str):
            librarydirectory = picked_dir

        if not librarydirectory:
            librarydirectory = "~/YTMediaTool/Downloads/"

        lm = tk.Label(frame, text = "Nykyinen kirjastokansio: " + librarydirectory)
        lm.config(font =("Courier", 14))
        lm.place(x=5, y = 5)


    def seldownloaddir1():
        global downloaddirectory
        global windowp
        windowp = tk.Toplevel(window)
        windowp.withdraw()
        picked_dir = filedialog.askdirectory()
        if isinstance(picked_dir, str):
            downloaddirectory1 = picked_dir

        if not downloaddirectory1:
            downloaddirectory1 = os.path.expanduser("~/YTMediaTool/Downloads/")

       # lm = tk.Label(frame, text = "Nykyinen latauskansio: " + downloaddirectory1)
        #lm.config(font =("Courier", 14))
        #lm.place(x=5, y = 5)


    def sellibrarydirectory():
        global librarydirectory1
        #librarydirectory = filedialog.askdirectory(mustexist=True)
        librarydirectory1 = fd.askopenfilename()
        print(librarydirectory1)
        librarydirectory.set(librarydirectory1)

        # Destination Directory
    tk.Label(frame, text="Destination directory: ").grid(row=2, column=1, sticky="E")

    downloaddirectory2 = tk.StringVar()
    downloaddirectory2.set(os.path.expanduser("~/YTMediaTool/Downloads/"))

    dirInputBox = tk.Entry(frame, textvariable=downloaddirectory2)
    dirInputBox.grid(row=2, column=2, sticky="WE")

    def seldir():
        global currentdirectory
        global windowp
        windowp = tk.Toplevel(window)
        windowp.withdraw()
        picked_dir = filedialog.askdirectory()
        if isinstance(picked_dir1, str) and len(picked_dir1) > 0:
            downloaddirectory2.set(picked_dir1)

    selectDirButton = tk.Button(frame, text="Pick...", command=seldir)
    selectDirButton.grid(row=2, column=3)


    tk.Label(frame, text="Library list directory: ").grid(row=20, column=1, sticky="E")

    librarydirectory = tk.StringVar()
    librarydirectory.set("Enter library file directory here.")

    dirInputBox = tk.Entry(frame, textvariable=librarydirectory)
    dirInputBox.grid(row=20, column=2, sticky="WE")

    def seldir():
        global currentdirectory
        global windowp
        windowp = tk.Toplevel(window)
        windowp.withdraw()
        picked_dir = librarydirectory1
        if isinstance(picked_dir2, str) and len(picked_dir2) > 0:
            librarydirectory.set(picked_dir2)

    selectDirButton = tk.Button(frame, text="Pick...", command=sellibrarydirectory)
    selectDirButton.grid(row=20, column=3)

    downloaddirectory = downloaddirectory1

    info = tk.Label(frame, text="SMLD is a tool designed to download large amounts of audio files from YouTube. Currently it works straight out of the box with iTunes library lists that you can get by CTRL + A and CTRL + C from the iTunes application. Put that in a text file and select it with the library list selector. Lists for other music services are coming soon " + u"\u2122", wraplength = 500 )
    info.place(x=40, y = 120)


    def runSMLD():
        global process1
        if os.path.isfile(librarydirectory1):
            cancelb.place(x=100, y = 66)
            with open(os.path.expanduser("~/YTMediaTool/Temp/downloaddirectory.txt"), "w") as f:
                f.write(downloaddirectory1)
                f.close()

            with open(os.path.expanduser("~/YTMediaTool/Temp/libraryfiledirectory.txt"), "w") as f:
                f.write(str(librarydirectory1))
                f.close()


            with open(os.path.expanduser("~/YTMediaTool/Temp/cancel.txt"), "w") as f:
                f.write("0")
                f.close()


            def loop_a():
                os.system('python SMLD.py')


            process1 = Process(target=loop_a)
            process1.start()






        else:
            messagebox.showinfo("File not found", f"File cannot be found or it doesn't exist. Please enter a valid file path.")


    #runSMLD = subprocess.run(['python', 'SMLD.py', arg1, arg2])
    libraryb=tk.Button(frame, text="Download", command=runSMLD).grid(row=30, column=0, sticky="E")


    def cancel():
        with open(os.path.expanduser("~/YTMediaTool/Temp/cancel.txt"), "w") as f:
            f.write("1")
            f.close()

        cancelb.place(x=100, y = 6600)


    cancelb=tk.Button(frame, text="Cancel", command=cancel)#.grid(row=30, column=0, sticky="E")



    def refresh():
        def loop_b():
            os.system("python SMLDprogressTracker.py")
        Process(target=loop_b).start()

        with open(os.path.expanduser("~/YTMediaTool/Temp/progress.txt"), "r") as f:
            progress = str(f.readlines())

            progress = progress.replace("[", "")
            progress = progress.replace("]", "")
            progress = progress.replace("'", "")
            progress = progress.replace("'", "")

            pg.config(text = "Progress: "+ str(progress) + "%")
            #print(progress)
            f.close()

    tk.Button(frame, text="Refresh progress", command=refresh).grid(row=30, column=2, sticky="E")

    pg = tk.Label(frame, text="Progress: "+ str(progress) + "%")
    pg.place(x=200, y = 70)

