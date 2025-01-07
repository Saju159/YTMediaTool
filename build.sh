#!/usr/bin/env bash
DISTPATH="$PWD/dist"
cd YTMediaTool || exit
pyinstaller -F Main.py --distpath "$DISTPATH" --noconsole --name YTMediaTool --hidden-import yt_dlp --hidden-import BasicPage --hidden-import SMLDpage --hidden-import SettingsPage --hidden-import AboutPage
cd ..
cp LICENSE dist/LICENSE # copy license to distribution
xdg-open dist
