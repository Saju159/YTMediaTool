set distpath=%CD%\dist-installer
cd WindowsInstaller
pyinstaller -F installer.py --distpath "%distpath%" --noconsole --name YTMediaTool-installer
cd ..
explorer dist-installer
