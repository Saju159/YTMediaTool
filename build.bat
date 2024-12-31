pyinstaller -F Main.py --hidden-import yt_dlp
copy "LICENSE" "dist\LICENSE"
explorer dist
