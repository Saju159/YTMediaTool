import os
from Common import getBaseConfigDir
from Settings import Settings
import SMLDpage
import time
import SMLD

track1 = 0

def trackprogress():
	global track1

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

	with open(os.path.join(getBaseConfigDir(),"SMLD", "Temp", "Songlist.txt"), 'r', encoding='utf-8') as file:
		tlines = file.readlines()
		file.close()

	edistyminen = (100 - (rlines / len(tlines) * 100))
	edistyminen2 = round(edistyminen, 2)
	track1 = float(len(tlines)-rlines)

	SMLDpage.progresstoshow =  edistyminen2
	SMLDpage.remainingtoshow = str(len(tlines)-rlines)
	SMLDpage.totaltoshow = str(len(tlines))

	if edistyminen2 == 100:
		if SMLD.cancel == False:
			print("valmis")
			check_status()

def writecancel():
	while True:
		print("Päällä")
		SMLDpage.cancel()

		if SMLD.cancel:
			print("cancel")
			break

def check_status():
	if SMLD.cancel == False:

		status = True
		threadcount = int(Settings["SMLD-mutithreading"])

		if not threadcount == 1:
			for i in range(threadcount):
				if not SMLD.donelist[i]:
					status = False
					break
		else:
			if SMLD.donelist[0]:
				status = False

		if status:
			SMLDpage.done = True
			writecancel()


def measurerate():
	start_time = time.time()
	while True:
		try:
			if SMLD.cancel:
				print("cancel")
				break

			elapsed_time = float(time.time() - start_time)
			time.sleep(5)
			rate = float(track1/(elapsed_time/60))
			rate = round(rate, 1)

			SMLDpage.rate = rate

		except Exception:
			print ("Rate calculation failed")





