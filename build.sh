#!/usr/bin/env bash
pyinstaller -F Main.py --noconsole --name YTMediaTool --hidden-import yt_dlp --hidden-import BasicPage --hidden-import SMLDpage --hidden-import SettingsPage --hidden-import AboutPage
cp LICENSE dist/LICENSE # copy license to distribution
xdg-open dist
