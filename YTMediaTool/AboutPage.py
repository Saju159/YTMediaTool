import tkinter as tk
import tkinter.font as font
from webbrowser import open_new_tab as openInBrowser
import Version

class Page(tk.Frame):
	def hidePage(self):
		self.Frame.place_forget()

	def showPage(self):
		self.Frame.place(y=34, relwidth=1.0)
		self.ParentWindow.after(1, lambda: self.ParentWindow.config(height=self.Frame.winfo_height()+34))

	def __init__(self, window: tk.Tk):
		self.ParentWindow = window

		self.Frame = tk.Frame(window, width=600, height=600)
		self.Frame.columnconfigure(0, weight=1)

		labels = {}

		labels["Title"] = tk.Label(self.Frame, text=f"{Version.Name} {Version.Version}", font=font.Font(size=24, weight="bold"))
		labels["Title"].grid(row=1, pady=10)
		labels["ShortDesc"] = tk.Label(self.Frame, text=Version.ShortDesc)
		labels["ShortDesc"].grid(row=2)
		labels["License"] = tk.Label(self.Frame, text=Version.GPLNotice)
		labels["License"].grid(row=3)
		labels["SourceCodeBtn"] = tk.Button(self.Frame, text="Source code:\nhttps://github.com/Saju159/YTMediaTool", command=lambda: openInBrowser("https://github.com/Saju159/YTMediaTool"))
		labels["SourceCodeBtn"].grid(row=4)
		labels["LicenseBtn"] = tk.Button(self.Frame, text="https://www.gnu.org/licenses/", command=lambda: openInBrowser("https://www.gnu.org/licenses/"))
		labels["LicenseBtn"].grid(row=5)

		def onResize(event):
			width = event.width - 20
			for label in labels:
				labels[label].config(wraplength=width)

		self.Frame.bind("<Configure>", onResize)
