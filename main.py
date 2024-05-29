from spotipy.oauth2 import SpotifyOAuth
from tkinter import scrolledtext
from langdetect import detect
import tkinter as tk
import lyricsgenius
import threading
import spotipy
import json
import time
import sys
import os

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
spotify = spotipy.Spotify(
    auth_manager=SpotifyOAuth(client_id=cid, client_secret=secret, redirect_uri=redirect_uri, scope=scope))


def get_resource_path(relative_path):

    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


icon_file = get_resource_path("SpotiLyricslogo.ico")


def get_current_song():
    try:
        track = spotify.current_user_playing_track()

        if track and 'item' in track and 'artists' in track['item']:
            if track.get('currently_playing_type') == "ad":
                print("The currently playing track is an ad.")
                raise Exception

            else:
                artists = ", ".join(artist['name'] for artist in track['item']['artists'])
                name = track["item"]["name"]
                name_id = track["item"]["id"]
                return artists, name, name_id

        else:
            raise Exception

    except Exception as e:
        print(f"{e}")
        error_root = tk.Tk()
        error_root.title("SpotiLyrics")
        error_root.iconbitmap(icon_file)
        error_root.geometry("500x200")
        error_root.config(bg="green")
        title = tk.Label(error_root, font=("Arial", 12), bg='green',
                         text='It seems AD is currently playing. '
                              'Or player not playing at all'
                              '\nIf you are using AD-blocker please reload page.'
                              '\n\nIf you are using spotify for desktop it might not work properly.')
        title.pack()
        error_root.mainloop()
        sys.exit()

def main():
    global name_id
    artist, name, name_id = get_current_song()
    if artist != "":
        print(f"Currently playing: {artist} - {name} - {name_id}")

        # Fetch lyrics
        try:
            song = genius.search_song(name, artist)
            if song:
                lyrics = song.lyrics
                # print("\nLyrics:")
                # print(lyrics)
                return lyrics, name, artist
            else:
                print("Could not find lyrics for the current song.")
        except Exception as e:
            print(f"An error occurred while fetching lyrics: {e}")


def detect_language(text):
    try:
        return detect(text)
    except:
        return None


def background_loop():
    print("background loop started")
    global name_id1
    while True:
        time.sleep(5)
        try:
            artist1, name1, name_id1 = get_current_song()
            if name_id != name_id1:
                print(f'song not same')
                next_button.pack(padx=5, pady=5)
            else:
                print(f'loop restarted')
                next_button.forget()
        except Exception as e:
            print(f"{e}")

def next_song():
    global name_id
    lyrics, name, artist = main()
    if lyrics:
        lang = f"language (detected): {detect_language(lyrics)}"
        print(lang)
        lyrics = f"{lang}\n\n{lyrics}"
        main_title.config(text=f"Lyrics for song:\n {name}\n by {artist}")
        lyrics_text.config(state="normal")
        lyrics_text.delete("1.0", "end")
        lyrics_text.insert("1.0", lyrics)
        lyrics_text.config(state="disabled")
        name_id = name_id1
        next_button.forget()  # Hide the "NEXT SONG DETECTED, SWITCH LYRICS?" button
    else:
        print("Could not find lyrics for the next song.")

if __name__ == '__main__':
    try:
        lyrics, name, artist = main()
        lang = f"language (detected): {detect_language(lyrics)}"
        print(lang)
        lyrics = f"{lang}\n\n{lyrics}"
    except TypeError:
        lyrics = "Lyrics wasn't found for this song"
        lang = ""
    except TimeoutError:
        lyrics = "Timeout, check your internet connection and try again"
        lang = ""
    lyrics = lyrics.replace("You might also like", "")
    lyrics = lyrics.replace("Embed", "")
    lyrics = lyrics.replace("ContributorsTranslationsRomanization", "")
    lyrics = lyrics.replace("TranslationsEnglishRomanization", "")
    lyrics = lyrics.replace("Contributors", "")
    root = tk.Tk()
    root.title("SpotiLyrics")

    root.iconbitmap(icon_file)
    root.geometry("500x600")
    root.resizable(False, False)
    root.minsize(500, 600)
    root.maxsize(500, 600)
    root.config(bg="green")
    next_button = tk.Button(root, bg='green', fg='black', text='NEXT SONG DETECTED, SWITCH LYRICS?',
                            command=next_song)
    background = threading.Thread(target=background_loop, daemon=True)
    background.start()
    try:
        main_title = tk.Label(text=f"Lyrics for song:\n {name}\n by {artist}", font=("Arial", 10, "bold"), bg='green')
        main_title.pack()
    except NameError:
        main_title = tk.Label(text=f"Error occured", font=("Arial", 10, "bold"), bg='green')
        main_title.pack()

    if lyrics:

        lyrics_frame = tk.Frame(root)
        lyrics_frame.pack(expand=True, fill='both')

        lyrics_text = scrolledtext.ScrolledText(lyrics_frame, wrap="word", bg="green", fg="black", font=("Arial", 17))
        lyrics_text.insert("1.0", lyrics)
        lyrics_text.config(state="disabled")
        lyrics_text.pack(expand=True, fill="both")
    elif lyrics == "Could not find lyrics for the current song." or lyrics == f"No results found for: '{name}'":
        lyrics_label = tk.Label(root, text="Lyrics not found.", bg="black", fg="white")
        lyrics_label.pack()
    else:
        lyrics_label1 = tk.Label(root, text="Exception raised.", bg="black", fg="white")
        lyrics_label1.pack()

    root.mainloop()
