import sys
import os
import json
import spotipy
import authenticate

access_token = authenticate.authenticate()

spotify = spotipy.Spotify(auth=access_token)  

with open('tracks.json') as f:
    tracks = json.load(f)

for i in range(0, len(tracks), 50):
    section = tracks[i:i + 50]
    spotify.current_user_saved_tracks_add(section) 
