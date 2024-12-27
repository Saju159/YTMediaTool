import tkinter as tk
from tkinter import filedialog
import subprocess
import os
from sys import platform

modenum = 1

window = tk.Tk()
window.title("YTMediaTool")
lbl = tk.Label(window, text="YTMediaTool")
window.geometry('600x400')
window.configure(bg='gray')

def getUserDownloadDir():
    if platform.startswith == "linux":
        c = subprocess.run(["which", "xdg-user-dir"])
        if c.returncode == 0:
            c = subprocess.run(["xdg-user-dir", "DOWNLOAD"])
            if c.returncode == 0 and c.stdout:
                return c.stdout

    # fallback to a 'Downloads' directory in the user's home
    return os.path.expanduser("~/Downloads")

currentdirectory = getUserDownloadDir()


lm = tk.Label(window, text = "Toimintatila:")
lm.config(font =("Courier", 14))
lm.place(x=5, y=5)

def show():
    tk.Label.config( text = mode.get() )

modes = [
    "URL lataus",
    "Lataus Hakusanalla",
]

mode = tk.StringVar()



l1, l2, download, seldirb, input1 = None, None, None, None, None

def selection():
    modenum = modes.index(mode.get())
    global l1, l2, download, seldirb, input1

    input1 = tk.Text(window, height = 1, width = 50)
    input1.place(x=110, y=60)

    downloadb=tk.Button(window, text="Lataa",bg="yellow", command=download)
    downloadb.place(x=5, y=90)

    seldirb=tk.Button(window, text="Valitse kohdekansio",bg="yellow", command=seldir)
    seldirb.place(x=80, y=90)



    if l1:
        l1.destroy()
    if l2:
        l2.destroy()

    if modenum == 0:
        l1 = tk.Label(window, text = "URL:")
        l1.config(font =("Courier", 14))
        l1.place(x=5, y=60)

        #l2.destroy()

    if modenum == 1:
        l2 = tk.Label(window, text = "Hakusana:")
        l2.config(font =("Courier", 14))
        l2.place(x=5, y=60)

        #l1.destroy()


drop = tk.OptionMenu( window , mode , *modes, command=lambda _: selection())
drop.pack()



def download():
    input2 = input1.get("1.0", "end").strip()

    if modenum == 0:
        filename = subprocess.getoutput(f'yt-dlp {input2} --print filename {input2}')
        ytcomman = [
            "yt-dlp",
            "-f", "ba[ext=m4a]",
            "-o", f"{currentdirectory}/{filename}.m4a",
            input2,
            "--max-downloads", "1"
        ]

    if modenum == 1:
        filename = subprocess.getoutput(f'yt-dlp "ytsearch:{input2}", --print filename {input2}')
        ytcomman = [
            "yt-dlp",
            "-f", "ba[ext=m4a]",
            "-o", f"{currentdirectory}/{filename}.m4a",
            f"ytsearch:{input2}",
            "--max-downloads", "1"
        ]

    subprocess.run(
        ytcomman, check=True, text=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=os.environ
    )

def seldir():
    global currentdirectory
    global windowp
    windowp = tk.Toplevel(window)
    windowp.withdraw()
    picked_dir = filedialog.askdirectory()
    if isinstance(picked_dir, str):
        currentdirectory = picked_dir

    lm = tk.Label(window, text = "Nykyinen kohdekansio: " + currentdirectory)
    lm.config(font =("Courier", 14))
    lm.place(x=5, y=130)



exit=tk.Button(window, text="Poistu",bg="yellow", command=quit)
exit.place(x=5, y=180)

def quit():
    window.destroy
    if windowp: windowp.destroy

window.mainloop()
quit()
