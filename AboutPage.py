import tkinter as tk
import tkinter.font as font
from webbrowser import open_new_tab as openInBrowser
import Version

def createFrame(window):
	global frame
	frame = tk.Frame(window, width=600, height=380)
	frame.columnconfigure(0, weight=1)

	labels = {}

	global showPage, hidePage
	def hidePage():
		frame.place_forget()
	def showPage():
		frame.place(y=34, h=-34, relwidth=1.0, relheight=1.0)

	labels["Title"] = tk.Label(frame, text=f"{Version.Name} {Version.Version}", font=font.Font(size=24, weight="bold"))
	labels["Title"].grid(row=1, pady=16)
	labels["ShortDesc"] = tk.Label(frame, text="Media downloader")
	labels["ShortDesc"].grid(row=2)
	labels["License"] = tk.Label(frame, text="(c) 2025 Saju159 & arttuc\nYTMediaTool is distributed under the terms of the GNU General Public License Version 3.0")
	labels["License"].grid(row=3)
	labels["SourceCodeBtn"] = tk.Button(frame, text="Source code:\nhttps://github.com/Saju159/YTMediaTool", command=lambda: openInBrowser("https://github.com/Saju159/YTMediaTool"))
	labels["SourceCodeBtn"].grid(row=4)

	def onResize(event):
		nonlocal labels
		width = event.width - 20
		for label in labels:
			labels[label].config(wraplength=width)

	frame.bind("<Configure>", onResize)
