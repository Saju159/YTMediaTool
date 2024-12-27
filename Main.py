import tkinter as tk
from tkinter import filedialog
import subprocess
import os
from sys import platform

page1rely = 0





window = tk.Tk()
window.title("YTMediaTool")
lbl = tk.Label(window, text="YTMediaTool")
window.geometry('600x400')
window.configure(bg='gray')

page1frame = tk.Frame(window, width=600, height=380)
page1frame.pack()


page1frame.place(y=4000)

lm = tk.Label(page1frame, text = "Toimintatila:")
lm.config(font =("Courier", 14))
lm.place(x=5, y=5)


def seldir():
        global currentdirectory
        global windowp
        windowp = tk.Toplevel(window)
        windowp.withdraw()
        picked_dir = filedialog.askdirectory()
        if isinstance(picked_dir, str):
            currentdirectory = picked_dir

        lm = tk.Label(page1frame, text = "Nykyinen kohdekansio: " + currentdirectory)
        lm.config(font =("Courier", 14))
        lm.place(x=5, y=page1rely + 130)



l1, l2, download, seldirb, input1 = None, None, None, None, None

input1 = tk.Text(page1frame, height = 1, width = 50)
input1.place(x=110, y=  60)

downloadb=tk.Button(page1frame, text="Lataa",bg="yellow", command=download)
downloadb.place(x=5, y= 90)

seldirb=tk.Button(page1frame, text="Valitse kohdekansio",bg="yellow", command=seldir)
seldirb.place(x=80, y= 90)








modenum = 1


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



def page1():
    page1frame.place(y=40)




    def show():
        tk.Label.config( text = mode.get() )

    modes = [
        "URL lataus",
        "Lataus Hakusanalla",
    ]

    mode = tk.StringVar()



    def selection():
        modenum = modes.index(mode.get())
        global l1, l2, download, seldirb, input1



        if l1:
            l1.destroy()
        if l2:
            l2.destroy()

        if modenum == 0:
            l1 = tk.Label(page1frame, text = "URL:")
            l1.config(font =("Courier", 14))
            l1.place(x=5, y=60)

            #l2.destroy()

        if modenum == 1:
            l2 = tk.Label(page1frame, text = "Hakusana:")
            l2.config(font =("Courier", 14))
            l2.place(x=5, y=60)

            #l1.destroy()


    drop = tk.OptionMenu( page1frame , mode , *modes, command=lambda _: selection())
    drop.place(x=155, y=0 )



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



def page2():
    toggle_button("Vaihtoehto 2")
    page1frame.place(y=4000)

def page3():
    toggle_button("Vaihtoehto 3")
    page1frame.place(y=4000)

def toggle_button(selected):
    current_value.set(selected)








exit=tk.Button(page1frame, text="Poistu",bg="yellow", command=quit)
exit.place(x=5, y= page1rely + 180)

def quit():
    window.destroy
    if windowp: windowp.destroy

current_value = tk.StringVar(value="None")

button1 = tk.Radiobutton(
    window,
    text="Basic",
    value="Vaihtoehto 1",
    variable=current_value,
    indicatoron=False,
    width=15,
    command=page1,
)
button1.place(x=5, y=5)


button2 = tk.Radiobutton(
    window,
    text="SMLD",
    value="Vaihtoehto 2",
    variable=current_value,
    indicatoron=False,
    width=15,
    command=page2,
)
button2.place(x=155, y=5)


button3 = tk.Radiobutton(
    window,
    text="About",
    value="Vaihtoehto 3",
    variable=current_value,
    indicatoron=False,
    width=15,
    command=page2,
)
button3.place(x=305, y=5)

def toggle_button(selected):
    current_value.set(selected)


window.mainloop()
quit()





