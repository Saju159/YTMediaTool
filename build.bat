pyinstaller -F Main.py --noconsole --name YTMediaTool --hidden-import yt_dlp --hidden-import BasicPage --hidden-import SMLDpage --hidden-import SettingsPage --hidden-import AboutPage
copy "LICENSE" "dist\LICENSE.txt"
explorer dist
