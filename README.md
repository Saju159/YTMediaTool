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
This tool works with many websites not listed here. These websites just have been confirmed working:
 - Facebook (Audio only)
 - Instagram 
 - Reddit
 - TikTok
 - X
 - Yle Areena
 - YouTube
 
## Usage
### Basic Page
 - The usage of the Basic Page is very simple. First select one of the operation modes. "Dowload from URL" -option uses yt-dlp to download a video or an audio file from a wide variety of websites. "Search & Download from YouTube" downloads the first result when you search the input from YouTube. 
 - You can clear the input box with the "C" button. 
 - To reduce downloading times, original format and source video quality is recommemded as the program does not need to convert the files to another format.
 - Downloading playlists does work, but currently you can not cancel the downloading process.

### SMLD
 - SMLD saves a download history to the home directory of your system (~/YTMediaTool/SMLD_History.txt).
 - SMLD adds metadata to the downloaded songs either from the input file or the Music Brainz API.
 - SMLD gives download rate as SPM (Songs Per Minute).
#### SMLD Page (Primary)
SMLD works with Spotify, iTunes and Youtube Music.
 - SMLD destination folder is the base folder where SMLD starts building the folder structure by artist and album.
 - You need to select a library list file using the Library list directory picker. Most common iTunes, Spotify and YouTube Music library lists are .CSV files and you can generate them using the tool linked under the input bar "Open .csv tool". In the tool select the service you want to download your library from (iTunes, Spotify or YouTube Music). Then input the link of a playlist to the URL box on the website. After that select "Choose Destination" and then "Export to file". Select the CSV format.
 - After downloading the file select it with the Library list file picker, select the format you want and start the download.
 NOTE: Metada can currently only be saved when using the m4a format.

#### SMLD Page extended library format
 - This library format only works with iTunes. This format can save favorite songs to a separate playlist and save the genre of the song.
 - This extended format is saved to a text file by first going to the iTunes application and select one song. Then CTRL + A and CTRL + C. Then open your prefered text editor and paste the contents there with CTRL + V. The file is done and you can select it with the Library list directory picker. This has been tested on the current iTunes windows version.
 
#### SMLD Quick Download Format
 - This format allows the user to download smaller quantities of songs at a time. 
 - This format has one major benefit to Basic Page. It adds metadata to songs. The program tries to get a name for the album from the Music Brainz API.
 - Simply select your download directory and SMLD will automatically create a file with instructions on how to use the format. Write the name of the artist and the song separated by a comma (ARTIST,SONG1,SONG2,SONG3...).

### Installation
Installation of this program is very simple. 
 - First download the binary from GitHub releases (Windows or linux).
 - Then you need to install FFmpeg and input the FFmpeg installation directory in the settings. Get FFmpeg from https://www.ffmpeg.org/download.html
 - After you download it FFmpeg binary itself is located in /ffmpeg-master-latest-win64-gpl/bin/ffmpeg.exe
NOTE: These are not installers and they work simply as a executable file as they are downloaded.
 
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
 - [FFmpeg](https://www.ffmpeg.org/) (runtime only)
 - kdialog (optional, linux only)
