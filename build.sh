#!/usr/bin/env bash
pyinstaller -F Main.py --noconsole --hidden-import yt_dlp
cp LICENSE dist/LICENSE # copy license to distribution
xdg-open dist
