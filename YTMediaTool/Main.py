from sys import argv

if len(argv) > 1 and argv[1] == "--version":
	import Version
	print(f"{Version.Name} {Version.Version} - {Version.ShortDesc}\n{Version.GPLNotice}")
	exit()

if __name__ == "__main__": # Only run if this is the main process.
	import os
	import tkinter as tk
	from Common import getBaseConfigDir
	import Settings
	from tkinter import messagebox

	if not os.path.exists(os.path.join(getBaseConfigDir(),"SMLD")):
		os.makedirs(os.path.join(getBaseConfigDir(),"SMLD"))

	if not os.path.exists(os.path.join(getBaseConfigDir(),"SMLD", "Temp")):
		os.makedirs(os.path.join(getBaseConfigDir(),"SMLD", "Temp"))

	with open(os.path.join(getBaseConfigDir(),"SMLD", "Temp", "progress.txt"), "w") as f:
		f.close()

	with open(os.path.join(getBaseConfigDir(),"SMLD", "Temp", "cancel.txt"), "w") as f:
		f.write("0")
		f.close()

	window = tk.Tk()
	window.title("YTMediaTool")
	# window.geometry('600x480')
	window.minsize(600, 34)
	window.resizable(width=True, height=False)

	tabFrame = tk.Frame(window, bg='gray')
	tabFrame.place(x=0, y=0, relwidth=1.0, height=34)
	tabFrame.rowconfigure(0, weight=1)

	pageNames = {
		"BasicPage": "Basic",
		"SMLDpage": "SMLD",
		"SettingsPage": "Settings",
		"AboutPage": "About"
	}
	pages = []

	def hideAllPages():
		for p in pages:
			p.hidePage()

	def showSelPage():
		hideAllPages()
		pages[currentPage.get()].showPage()

	currentPage = tk.IntVar(value=0)

	i = 0
	for pageName in pageNames.keys():
		page = __import__(pageName)
		page.createFrame(window)

		pages.insert(i, page)

		pageTabBtnFrame = tk.Frame(tabFrame)
		pageTabBtnFrame.grid(row=0, column=i, sticky="NSWE", padx=5, pady=5)
		tabFrame.columnconfigure(i, weight=1)

		pageTabBtn = tk.Radiobutton(pageTabBtnFrame, text=pageNames[pageName], value=i, variable=currentPage, indicatoron=False, command=showSelPage)
		pageTabBtn.place(relwidth=1.0, relheight=1.0)

		i += 1

	def quit():
		with open(os.path.join(getBaseConfigDir(),"SMLD", "Temp", "cancel.txt"), "w") as f:
			f.write("1")
			f.close()
		window.destroy
		Settings.saveSettingsToFile()

	window.after(1, lambda: pages[0].showPage())

	if not os.path.isfile(Settings.Settings["FFmpeg_path"]):
		messagebox.showinfo("FFmpeg not found", f'FFmpeg cannot be found in: "{Settings.Settings["FFmpeg_path"]}". Please enter a valid FFmpeg path in the settings.')

	window.mainloop()
	quit()
