set distpath=%CD%\dist
cd YTMediaTool
pyinstaller -F Main.py --distpath "%distpath%" --noconsole --name YTMediaTool --hidden-import yt_dlp --hidden-import BasicPage --hidden-import SMLDpage --hidden-import SettingsPage --hidden-import AboutPage
cd ..
copy "LICENSE" "dist\LICENSE.txt"
explorer dist
