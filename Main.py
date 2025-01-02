import tkinter as tk
import Settings


import os

librarydirectory = os.path.expanduser("~/YTMediaTool/")

if not os.path.exists(librarydirectory + "Temp/"):
    os.makedirs(librarydirectory + "Temp/")

if not os.path.exists(librarydirectory + "Librarylist/"):
    os.makedirs(librarydirectory + "Librarylist/")

if not os.path.exists(librarydirectory + "Downloads/"):
    os.makedirs(librarydirectory + "Downloads/")

with open(os.path.expanduser("~/YTMediaTool/Temp/progress.txt"), "w") as f:
    f.close()

import SettingsPage # Import settings page before anything else
with open(os.path.expanduser("~/YTMediaTool/Temp/cancel.txt"), "w") as f:
            f.write("0")
            f.close()

import BasicPage
import SMLDpage


page1rely = 0

window = tk.Tk()
window.title("YTMediaTool")
lbl = tk.Label(window, text="YTMediaTool")
window.geometry('600x400')
window.configure(bg='gray')

page1frame = BasicPage.createFrame(window)
page2frame = SMLDpage.createFrame(window)
page3frame = SettingsPage.createFrame(window)

def page1():
    BasicPage.showPage()
    SMLDpage.hidePage()
    SettingsPage.hidePage()

def page2():
    toggle_button("Vaihtoehto 2")
    BasicPage.hidePage()
    SMLDpage.showPage()
    SettingsPage.hidePage()

def page3():
    toggle_button("Vaihtoehto 3")
    BasicPage.hidePage()
    SMLDpage.hidePage()
    SettingsPage.showPage()

def page4():
    toggle_button("Vaihtoehto 4")
    BasicPage.hidePage()
    SMLDpage.hidePage()
    SettingsPage.hidePage()

def toggle_button(selected):
    current_value.set(selected)

current_value = tk.StringVar(value="Vaihtoehto 1")

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
    text="Settings",
    value="Vaihtoehto 3",
    variable=current_value,
    indicatoron=False,
    width=15,
    command=page3,
)
button3.place(x=305, y=5)

button4 = tk.Radiobutton(
    window,
    text="About",
    value="Vaihtoehto 4",
    variable=current_value,
    indicatoron=False,
    width=15,
    command=page4,
)
button4.place(x=455, y=5)

def quit():
    with open(os.path.expanduser("~/YTMediaTool/Temp/cancel.txt"), "w") as f:
        f.write("1")
        f.close()
    window.destroy
    Settings.saveSettingsToFile()

window.after(1,page1)

window.mainloop()
quit()





