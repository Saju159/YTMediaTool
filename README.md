# YTMediaTool

YTMediaTool is a tool designed to download large and small quantities of video and audio files from YouTube. It is powered by yt-dlp and mutagen. 

(c) 2025 Saju159 & arttuc

YTMediaTool is licensed under the terms of the GNU General Public License Version 3.0

## Features
 - Download different video formats from a wide selection.
 - Select from multiple audio formats to download.
 - Download by keyword or with a provided link.
 - Download HUGE music collections with SMLD from YouTube or Spotify.
 
### Verified websites that works with Basic page
 - Reddit
 - Yle Areena
 - YouTube
 
## Usage
### Basic Page
 - The usage of the Basic Page is very simple. First select one of the operation modes. "Dowload from URL" -option uses yt-dlp to download a video or an audio file from a wide variety of websites. "Search & Download from YouTube" downloads the first result when you search the input from YouTube. 
 - You can clear the input box with the "C" button. 
 - To reduce downloading times, original format and source video quality is recommemded as the program does not need to convert the files to another format.

### SMLD Page (Primary)
 - SMLD destination folder is the base folder where SMLD starts building the folder structure by artist and album.
 - You need to select a library list file using the Library list directory picker. Most common iTunes and Spotify library lists are .CSV files and you can generate them using the tool linked under the input bar "Open .csv tool". In the tool select the service you want to download your library from (iTunes or Spotify). Then input the link of a playlist to the URL box on the website. After that select "Choose Destination" and then "Export to file". Select the CSV format.
 - After downloading the file select it with the Library list file picker, select the format you want and start the download.
 NOTE: Metada can currently only be saved when using the m4a format.

### SMLD Page extended library format
 - This library format only works with iTunes. This format can save favorite songs to a separate playlist and save the genre of the song.
 - This extended format is saved to a text file by first going to the iTunes application and select one song. Then CTRL + A and CTRL + C. Then open your prefered text editor and paste the contents there with CTRL + V. The file is done and you can select it with the Library list directory picker. This has been tested on the current iTunes windows version.

## Configuration
The program is configured in the 'Settings' tab within the interface.

Config files are written to:
 - Linux: `$XDG_CONFIG_HOME/YTMediaTool/` or `~/.config/YTMediaTool/`
 - Windows: `%USERPROFILE%\AppData\Roaming\YTMediaTool\` (previously `%USERPROFILE%\AppData\Local\Roaming\YTMediaTool\`
 - Other OSes: `~/.YTMediaTool/`

## Building
The program is compiled to a single executable using [PyInstaller](https://pypi.org/project/pyinstaller/).

The binaries in the releases are currently made by using the included build scripts in Arch Linux and a Windows 10 VM.

### Dependencies
 - [Python 3.13.1](https://www.python.org/downloads/) (untested on older releases)
 - tk
 - [yt-dlp](https://github.com/yt-dlp/yt-dlp)
 - [mutagen](https://github.com/quodlibet/mutagen)
 - [ffmpeg](https://www.ffmpeg.org/) (runtime only)
 - kdialog (optional, linux only)
