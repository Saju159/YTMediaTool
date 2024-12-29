import SMLDpage
import time
import os


with open(os.path.expanduser("~/YTMediaTool/Temp/libraryfiledirectory.txt")) as f:
    libraryfiledirectory = f.read()
    f.close()

with open(os.path.expanduser("~/YTMediaTool/Temp/Songlist.txt"), 'r', encoding='utf-8') as file:
    rlines = file.readlines()
    file.close()


with open(os.path.expanduser(libraryfiledirectory), 'r', encoding='utf-8') as file:
    tlines = file.readlines()
    file.close()


#print("Rivejä on jäljellä: " + str(len(rlines)))
#print("Rivejä on yhteensä: " + str(len(tlines)))

edistyminen = (100 - (len(rlines) / len(tlines) * 100))
edistyminen2 = round(edistyminen, 2)
print("Edistyminen: " + str(edistyminen2) + "%")

with open(os.path.expanduser("~/YTMediaTool/Temp/progress.txt"), "w") as f:
    f.write(str(edistyminen2))
    f.close()



