import spotipy
from spotipy.oauth2 import SpotifyOAuth
from pprint import pprint
import lyricsgenius
import json

# config file
file = open('config.json', 'r')
config = json.load(file)

# api
genius = lyricsgenius.Genius(config['GENIUS_ACCESS_TOKEN'])
cid = config['CLIENT_ID']
secret = config['CLIENT_SECRET']
redirect_uri = 'http://localhost:7777/callback'
scope = 'user-read-currently-playing'

# spotify auth
spotify = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=cid,
                                               client_secret=secret,
                                               redirect_uri=redirect_uri,
                                               scope=scope))

def get_current_song():
    track = spotify.current_user_playing_track()
    pprint(track)
    if track and 'item' in track and 'artists' in track['item']:
        artists = ", ".join(artist['name'] for artist in track['item']['artists'])
        name = track["item"]["name"]
        name_id = track["item"]["id"]
        return artists, name, name_id
    else:
        return None, None, None

def main():
    artist, name, name_id = get_current_song()
    if artist !="":
        print(f"Currently playing: {artist} - {name} - {name_id}")

        # Fetch lyrics
        try:
            song = genius.search_song(name, artist)
            if song:
                lyrics = song.lyrics
                print("\nLyrics:")
                print(lyrics)
            else:
                print("Could not find lyrics for the current song.")
        except Exception as e:
            print(f"An error occurred while fetching lyrics: {e}")

if __name__ == '__main__':
    main()
    input()
