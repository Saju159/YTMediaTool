import tkinter as tk
import tkinter.font as font
from webbrowser import open_new_tab as openInBrowser
import Version

def createFrame(window):
	global frame
	frame = tk.Frame(window, width=600, height=600)
	frame.columnconfigure(0, weight=1)

	labels = {}

	global showPage, hidePage
	def hidePage():
		frame.place_forget()
	def showPage():
		frame.place(y=34, relwidth=1.0)
		window.after(1, lambda: window.config(height=frame.winfo_height()+34))

	labels["Title"] = tk.Label(frame, text=f"{Version.Name} {Version.Version}", font=font.Font(size=24, weight="bold"))
	labels["Title"].grid(row=1, pady=10)
	labels["ShortDesc"] = tk.Label(frame, text=Version.ShortDesc)
	labels["ShortDesc"].grid(row=2)
	labels["License"] = tk.Label(frame, text=Version.GPLNotice)
	labels["License"].grid(row=3)
	labels["SourceCodeBtn"] = tk.Button(frame, text="Source code:\nhttps://github.com/Saju159/YTMediaTool", command=lambda: openInBrowser("https://github.com/Saju159/YTMediaTool"))
	labels["SourceCodeBtn"].grid(row=4)
	labels["LicenseBtn"] = tk.Button(frame, text="https://www.gnu.org/licenses/", command=lambda: openInBrowser("https://www.gnu.org/licenses/"))
	labels["LicenseBtn"].grid(row=5)

	def onResize(event):
		nonlocal labels
		width = event.width - 20
		for label in labels:
			labels[label].config(wraplength=width)

	frame.bind("<Configure>", onResize)
