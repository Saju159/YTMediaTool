import os
from Common import getBaseConfigDir
from Settings import Settings

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


