import os
from Common import getBaseConfigDir
from Settings import Settings
import SMLDpage
import time

track1 = 0

def trackprogress():
	global track1

	with open(os.path.join(getBaseConfigDir(),"SMLD", "Temp", "libraryfiledirectory.txt")) as f:
		libraryfiledirectory = f.read()
		f.close()

	rlines = 0
	threadnumber = 0
	threadcount = int(Settings["SMLD-mutithreading"])

	if not threadcount == 1:
		threadcount = (int(Settings["SMLD-mutithreading"]))
		for threadnumber in range(threadcount):
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
	track1 = len(tlines)-rlines

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

def writecancel():
	while True:
		print("Päällä")
		SMLDpage.cancel()

		with open(os.path.join(getBaseConfigDir(),"SMLD", "Temp", "cancel.txt"), "r") as f:
			cancel = f.read()
			f.close()
			if int(cancel) == 1:
				print("cancel")
				break



def check_status():
	with open(os.path.join(getBaseConfigDir(),"SMLD", "Temp", "cancel.txt"), "r") as f:
		cancel = f.read()
		f.close()
	if int(cancel) == 0:
		#print("Totta")

		directory = os.path.join(getBaseConfigDir(),"SMLD", "Temp")
		status = True

		threadcount = int(Settings["SMLD-mutithreading"])

		if not threadcount == 1:
			for i in range(threadcount):
				file_path = os.path.join(directory, f"Done{i}.txt")

				if os.path.exists(file_path):
					with open(file_path, "r") as file:
						content = file.read().strip()
						if content == "0":
							status = False
							break

		else:
			file_path = os.path.join(directory, "Done0.txt")
			with open(file_path, "r") as file:
				content = file.read().strip()
				if content == "1":
					status = False

		if status:
			with open(os.path.join(getBaseConfigDir(),"SMLD", "Temp", "Done.txt"), "w") as f:
				f.write("1")
				f.close()
			writecancel()


def measurerate():
	start_time = time.time()
	time.sleep(30)
	while True:
		try:
			with open(os.path.join(getBaseConfigDir(),"SMLD", "Temp", "cancel.txt"), "r") as f:
				cancel = f.read()
				f.close()
				if int(cancel) == 1:
					print("cancel")
					break

			elapsed_time = int(time.time() - start_time)
			time.sleep(5)
			rate = track1/(elapsed_time/60)
			rate = round(rate, 0)

			with open(os.path.join(getBaseConfigDir(),"SMLD", "Temp", "rate.txt"), "w") as f:
				f.write(str(rate))
				f.close()

		except Exception:
			print ("Rate calculation failed")





