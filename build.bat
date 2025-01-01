pyinstaller -F Main.py --noconsole --hidden-import yt_dlp
copy "LICENSE" "dist\LICENSE"
explorer dist
