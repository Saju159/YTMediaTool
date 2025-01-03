import tkinter as tk
import Settings
from Common import getBaseConfigDir


import os

librarydirectory = os.path.expanduser("~/YTMediaTool/")

if not os.path.exists(librarydirectory + "Downloads/"):
    os.makedirs(librarydirectory + "Downloads/")

if not os.path.exists(os.path.join(getBaseConfigDir(),"SMLD")):
    os.makedirs(os.path.join(getBaseConfigDir(),"SMLD"))

if not os.path.exists(os.path.join(getBaseConfigDir(),"SMLD", "Temp")):
    os.makedirs(os.path.join(getBaseConfigDir(),"SMLD", "Temp"))


with open(os.path.join(getBaseConfigDir(),"SMLD", "Temp", "progress.txt"), "w") as f:
    f.close()

import SettingsPage # Import settings page before anything else
with open(os.path.join(getBaseConfigDir(),"SMLD", "Temp", "cancel.txt"), "w") as f:
    f.write("0")
    f.close()



import BasicPage
import SMLDpage
import AboutPage


page1rely = 0

window = tk.Tk()
window.title("YTMediaTool")
lbl = tk.Label(window, text="YTMediaTool")
window.geometry('600x400')
window.configure(bg='gray')

page1frame = BasicPage.createFrame(window)
page2frame = SMLDpage.createFrame(window)
page3frame = SettingsPage.createFrame(window)
page4frame = AboutPage.createFrame(window)

def page1():
    BasicPage.showPage()
    SMLDpage.hidePage()
    SettingsPage.hidePage()
    AboutPage.hidePage()

def page2():
    toggle_button("Vaihtoehto 2")
    BasicPage.hidePage()
    SMLDpage.showPage()
    SettingsPage.hidePage()
    AboutPage.hidePage()

def page3():
    toggle_button("Vaihtoehto 3")
    BasicPage.hidePage()
    SMLDpage.hidePage()
    SettingsPage.showPage()
    AboutPage.hidePage()

def page4():
    toggle_button("Vaihtoehto 4")
    BasicPage.hidePage()
    SMLDpage.hidePage()
    SettingsPage.hidePage()
    AboutPage.showPage()

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
    with open(os.path.join(getBaseConfigDir(),"SMLD", "Temp", "cancel.txt"), "w") as f:
        f.write("1")
        f.close()
    window.destroy
    Settings.saveSettingsToFile()

window.after(1,page1)

window.mainloop()
quit()





