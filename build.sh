#!/usr/bin/env bash
pyinstaller -F Main.py --hidden-import yt_dlp
xdg-open dist
