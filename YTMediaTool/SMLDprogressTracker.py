import os
from Common import getBaseConfigDir
from Settings import Settings
from tkinter import messagebox
import SMLDpage

def trackprogress():

	with open(os.path.join(getBaseConfigDir(),"SMLD", "Temp", "libraryfiledirectory.txt")) as f:
		libraryfiledirectory = f.read()
		f.close()

	rlines = 0
	i = 0
	threadnumber = int(Settings["SMLD-mutithreading"])

	if not threadnumber == 1:
		threadnumber = (int(Settings["SMLD-mutithreading"])-1)
		for i in range(threadnumber):
			with open(os.path.join(getBaseConfigDir(),"SMLD", "Temp", "Songlist" + str(threadnumber) + ".txt"), 'r', encoding='utf-8') as file:
				threadrlines = file.readlines()
				file.close()
			rlines = rlines + len(threadrlines)
	else:
		with open(os.path.join(getBaseConfigDir(),"SMLD", "Temp", "Songlist0.txt"), 'r', encoding='utf-8') as file:
			rlines = len(file.readlines())
			file.close()

	with open(os.path.expanduser(libraryfiledirectory), 'r', encoding='utf-8') as file:
		tlines = file.readlines()
		file.close()


	edistyminen = (100 - (rlines / len(tlines) * 100))
	edistyminen2 = round(edistyminen, 2)

	with open(os.path.join(getBaseConfigDir(),"SMLD", "Temp", "progress.txt"), "w") as f:
		f.write(str(edistyminen2) + "\n" + str(len(tlines)-rlines) + "\n" + str(len(tlines)))
		f.close()

	if edistyminen2 == 100:
		with open(os.path.join(getBaseConfigDir(),"SMLD", "Temp", "cancel.txt"), "r") as f:
			cancel = f.read()
			f.close()
		if int(cancel) == 0:
			print("valmis")
			check_status()


def check_status():
	with open(os.path.join(getBaseConfigDir(),"SMLD", "Temp", "cancel.txt"), "r") as f:
		cancel = f.read()
		f.close()
	if int(cancel) == 0:

		directory = os.path.join(getBaseConfigDir(),"SMLD", "Temp")
		status = True

		threadcount = int(Settings["SMLD-mutithreading"])
		for i in range(threadcount):
			file_path = os.path.join(directory, f"Done{i}.txt")

			if not os.path.exists(file_path):
				status = False
				break

			with open(file_path, "r") as file:
				content = file.read().strip()
				if content == "0":
					status = False
					break

		if status:
			with open(os.path.join(getBaseConfigDir(),"SMLD", "Temp", "Done.txt"), 'w') as f:
				f.write("1")
				f.close()
			with open(os.path.join(getBaseConfigDir(),"SMLD", "Temp", "cancel.txt"), "w") as f:
				f.write("1")
				f.close()

			SMLDpage.cancel()

			messagebox.showinfo("Done", "Downloading has been completed")






