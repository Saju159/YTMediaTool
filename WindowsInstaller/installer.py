import urllib.request, urllib.error, ssl, hashlib, zipfile, io, subprocess, os, shutil, threading
from sys import platform
from pathlib import Path
import tkinter as tk
import tkinter.messagebox as tkmsg
import tkinter.ttk as ttk

# Change these to the release tag that will be downloaded
Tag = "v0.4"
SHA256 = "14ccc349c835595879235595ba730d75d771b7aa96f4a2f6772b862f9af337ee"
# -------------------------------------------------------

DownloadURL = f"https://github.com/Saju159/YTMediaTool/releases/download/{Tag}/YTMediaTool-{Tag}-win32.zip"
InstallPath = platform == "win32" and Path(Path.home(), "AppData\\Roaming\\YTMediaTool\\Installation") or Path(Path.home(), "ytmediatool_install")
ExecFileName = "YTMediaTool.exe"

DesktopLnkPath = Path(Path.home(), "Desktop", "YTMediaTool.lnk")
MenuLnkPath = Path(Path.home(), "AppData", "Roaming", "Microsoft", "Windows", "Start Menu", "Programs", "YTMediaTool", "YTMediaTool.lnk")

status = ""
done = None
err = ""
def printstatus(s):
	global status
	status = s
	print(s)

def createWinLnk(execPath=Path, shortcutPath=Path):
	if platform != "win32":
		print(f"skipping windows shortcut creation on non-win32 platform:\n - execPath: {execPath}\n - shortcutPath: {shortcutPath}")
		return

	# https://stackoverflow.com/questions/9701840/create-a-shortcut-lnk-file-using-powershell/#9701907
	subprocess.run(["powershell", "-Command", f"$s = New-Object -COMObject WScript.Shell; $f = $s.CreateShortcut(\"{os.path.abspath(shortcutPath)}\"); $f.TargetPath = \"{os.path.abspath(execPath)}\"; $f.Save()"])

def GetInstalledVer():
	if InstallPath.is_dir():
		if Path(InstallPath, "ver").is_file():
			with open(Path(InstallPath, "ver"), "r") as f:
				return f.read()
	return None

def Uninstall(isSelf=True):
	if GetInstalledVer() != None:
		printstatus(f"Uninstalling {GetInstalledVer()}...")
		if InstallPath.is_dir(): shutil.rmtree(InstallPath)
		if DesktopLnkPath.is_file(): os.remove(DesktopLnkPath)
		if MenuLnkPath.is_file(): os.remove(MenuLnkPath)
		printstatus("Uninstalled!")
		if isSelf:
			global done
			done = 0
		return 0

def RunTask(createDesktopShortcut=True, createMenuShortcut=True):
	Uninstall(False)
	global done, err
	try:
		printstatus(f"Downloading from '{DownloadURL}'...")
		try:
			ctx = ssl.create_default_context()
			response = urllib.request.urlopen(DownloadURL, context=ctx)
		except Exception as err2:
			print(f"Failed to download: {err2}")
			done, err = 1, f"Failed to download: {err2}"
			return 1

		data = response.read()

		printstatus("Verifying...")
		print(f"Expected SHA256 Hash: {SHA256}")

		fHash = hashlib.sha256(data).hexdigest()
		print(f"Received SHA256 Hash: {fHash}")
		if SHA256 != fHash:
			print("Hashes do not match!")
			done, err = 1, f"SHA256 hashes do not match!\nExpected: {SHA256}\nGot: {fHash}"
			return 1

		printstatus("Unpacking...")
		Path.mkdir(InstallPath, parents=True, exist_ok=True)
		with zipfile.ZipFile(io.BytesIO(data), mode="r") as zf:
			zf.extractall(path=InstallPath)

		printstatus("Finishing up...")
		with open(Path(InstallPath, "ver"), "w") as f:
			f.write(Tag)

		printstatus("Creating shortcuts...")
		if createDesktopShortcut:
			createWinLnk(Path(InstallPath, ExecFileName), DesktopLnkPath)
		if createMenuShortcut:
			createWinLnk(Path(InstallPath, ExecFileName), MenuLnkPath)

		printstatus("Installed!")
		done = 0
		return 0

	except Exception as err2:
		done, err = 2, f"Installation failed: {err2}"
		return 2



if __name__ == "__main__":
	if platform != "win32":
		print("NOTE: This installer script is designed for Windows-platforms! It will not install the version for your system!")

	window = tk.Tk()
	window.title(f"YTMediaTool Installer for {Tag}")
	window.geometry("400x180")
	window.resizable(width=False, height=False)
	window.rowconfigure(0, weight=1)
	window.columnconfigure(0, weight=1)

	iVer = GetInstalledVer()
	print(iVer)

	statusTxt = tk.Label(window, text=f"Program for installing or upgrading YTMediaTool {Tag}\n\nInstalled version: {iVer or "not installed"}", wraplength=312)
	statusTxt.grid(row=0, column=0, sticky="NSWE", padx=4, pady=4)

	def updStatus():
		statusTxt.config(text=status)
		if done == 0:
			tkmsg.showinfo("Install success", f"Successfully installed YTMediaTool {Tag}!\nA shortcut has been created on your desktop and start menu.")
			window.quit()
		elif done == 1 or done == 2:
			tkmsg.showerror("Error", f"{err}")
			window.quit()
		else:
			window.after(16, updStatus)

	def updStatusUninstall():
		statusTxt.config(text=status)
		if done == 0:
			tkmsg.showinfo("Uninstall success", "Uninstalled YTMediaTool!")
			window.quit()
		elif done == 1 or done == 2:
			tkmsg.showerror("Error", f"{err}")
			window.quit()
		else:
			window.after(16, updStatusUninstall)

	def installBtnF():
		installBtn.config(state="disabled")
		uninstallBtn.config(state="disabled")

		t = threading.Thread(target=RunTask)
		t.start()
		window.after(16, updStatus)

	def uninstallBtnF():
		installBtn.config(state="disabled")
		uninstallBtn.config(state="disabled")

		t = threading.Thread(target=Uninstall)
		t.start()
		window.after(16, updStatusUninstall)

	installBtn = ttk.Button(window, text=iVer and (iVer == Tag and f"Reinstall YTMediaTool {Tag}" or f"Upgrade to YTMediaTool {Tag}") or f"Install YTMediaTool {Tag}", command=installBtnF)
	installBtn.grid(row=1, column=0, sticky="WE", padx=4, pady=4)

	uninstallBtn = ttk.Button(window, text="Uninstall YTMediaTool", command=uninstallBtnF)
	uninstallBtn.grid(row=2, column=0, sticky="WE", padx=4, pady=4)
	if not iVer:
		uninstallBtn.config(state="disabled")

	window.mainloop()
