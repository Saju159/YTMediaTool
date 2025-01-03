import os
from Common import getBaseConfigDir

def trackprogress():
    with open(os.path.join(getBaseConfigDir(),"SMLD", "Temp", "libraryfiledirectory.txt")) as f:
        libraryfiledirectory = f.read()
        f.close()

    with open(os.path.join(getBaseConfigDir(),"SMLD", "Temp", "Songlist.txt"), 'r', encoding='utf-8') as file:
        rlines = file.readlines()
        file.close()


    with open(os.path.expanduser(libraryfiledirectory), 'r', encoding='utf-8') as file:
        tlines = file.readlines()
        file.close()


    edistyminen = (100 - (len(rlines) / len(tlines) * 100))
    edistyminen2 = round(edistyminen, 2)
    print("Edistyminen: " + str(edistyminen2) + "%")

    with open(os.path.join(getBaseConfigDir(),"SMLD", "Temp", "progress.txt"), "w") as f:
        f.write(str(edistyminen2) + "\n" + str(len(tlines)-len(rlines)) + "\n" + str(len(tlines)))
        f.close()


