import re
from ytmusicapi import YTMusic

def extract_playlist_id(playlist_url):
    """Extracts the playlist ID from the provided URL."""
    pattern = r'(?<=list=)[^&]+'
    match = re.search(pattern, playlist_url)
    return match.group(0) if match else None

def ytmusicurl(playlist_url):
    #"""Retrieves song, artist, and album information from the playlist."""
    ytmusic = YTMusic()
    playlist_id = extract_playlist_id(playlist_url)
    if not playlist_id:
        print("Invalid playlist URL")
        return

    # Fetch playlist items
    playlist_items = ytmusic.get_playlist(playlist_id)['tracks']

    if not playlist_items:
        print("No songs found in the playlist.")
        return
    else:

        # Print the details of each song
        for track in range(len(playlist_items)):
            #print(str(playlist_items[track]) + "\n")
            video_id = playlist_items[track]['videoId'].strip()
            song_title = playlist_items[track]['title'].strip()
            artist = playlist_items[track]['artists']
            album = playlist_items[track]['album']

            artist = str(artist).split(":")[1].split(",")[0].replace("'", "").strip()
            if not album == None:
                album = str(album).split(":")[1].split(",")[0].replace("'", "").strip()
            else:
                album = "[Unkown Album]"
            
            print(f"Video id: {video_id}")
            print(f"Song: {song_title}")
            print(f"Artist(s): {artist}")
            print(f"Album: {album}\n")

if __name__ == "__main__":
    playlist_url = "https://music.youtube.com/playlist?list=PLjCT52YyPOMTyaAfVNB0DLbJYON2rAkbh" #input("Enter the YouTube Music playlist URL: ")
    ytmusicurl(playlist_url)
