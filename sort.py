import sys
import os
import json
import itertools
import time
import argparse

import spotipy

import authenticate


def get_tracks():
    tracks = []
    saved_tracks = spotify.current_user_saved_tracks(limit=50, offset=0)

    for item in saved_tracks['items']:
        tracks.append(item['track'])

    remaining_tracks = saved_tracks['total'] - len(tracks)

    while remaining_tracks > 0:
        saved_tracks = spotify.current_user_saved_tracks(limit=50, offset=len(tracks))
        for item in saved_tracks['items']:
            tracks.append(item['track'])
        remaining_tracks = saved_tracks['total'] - len(tracks)
    return tracks


def group_tracks_artist(tracks):
    artists = []
    for track in tracks:
        artists.append(track['artists'][0]['id'])
    artists = sorted(set(artists), key=artists.index)

    tracks_grouped_artist = []  

    for artist in artists:
        artist_tracks = []
        for track in tracks:
            if track['artists'][0]['id'] == artist:
                artist_tracks.append(track)
        tracks_grouped_artist.append(artist_tracks)
    return tracks_grouped_artist


def group_tracks_album(tracks):
    albums = []
    for track in tracks:
        albums.append(track['album']['id'])
    albums = sorted(set(albums), key=albums.index)
    
    tracks_grouped_album = []

    for album in albums:
        album_tracks = []
        for track in tracks:
            if track['album']['id'] == album:
                album_tracks.append(track)
        tracks_grouped_album.append(album_tracks)
    return tracks_grouped_album


def reorder_groups(groups, category):
    print("\n")
    for index, group in enumerate(groups):
        if category == "artists":
            print(f"{index}: {group[0]['artists'][0]['name']}")
        elif category == "albums":
            print(f"{index}: {group[0]['album']['name']}")
        elif category == "tracks":
            print(f"{index}: {group['name']}")

    command = input("Enter two numbers: ")
    if command == "":
        print("Continuing")
        return groups
    elif command == "quit" or command == "q":
        sys.exit()

    command = command.split()
    if len(command) != 2:
        print("Did not enter two numbers")
        reorder_groups(groups, category)

    else:
        move = groups.pop(int(command[0]))
        groups.insert(int(command[1]), move)

        return reorder_groups(groups, category)


def degroup_tracks(grouped_tracks):
    degrouped_tracks = []
    for track_group in grouped_tracks:
        for track in track_group:
            degrouped_tracks.append(track)
    return degrouped_tracks


def get_uris(tracks):
    track_uris = []
    for track in tracks:
        track_uris.append(track['uri'])
    return track_uris


def remove_tracks(track_uris):
    for i in range(0, len(track_uris), 50):
        section = track_uris[i:i + 50]
        spotify.current_user_saved_tracks_delete(section) 


def add_tracks(track_uris):
    for track in track_uris:
        spotify.current_user_saved_tracks_add([track]) 
        time.sleep(1)


parser = argparse.ArgumentParser()
parser.add_argument('-A', '--artists', action='store_true', help='Reorder artists')
parser.add_argument('-a', '--albums', action='store_true', help='Reorder albums')
parser.add_argument('-t', '--tracks', action='store_true', help='Reorder tracks')
args = parser.parse_args()

access_token = authenticate.authenticate()
spotify = spotipy.Spotify(auth=access_token)  

tracks = get_tracks()
unsorted_tracks = tracks[:]

with open('tracks.json', 'w') as f:
    json.dump(tracks, f)

if args.artists:
    tracks_grouped_artist = group_tracks_artist(tracks)
    tracks_grouped_artist = reorder_groups(tracks_grouped_artist, "artists")
    tracks = degroup_tracks(tracks_grouped_artist)

if args.albums:
    tracks_grouped_album = group_tracks_album(tracks)
    tracks_grouped_album = reorder_groups(tracks_grouped_album, "albums")
    tracks = degroup_tracks(tracks_grouped_album)

if args.tracks:
    tracks = reorder_groups(tracks, "tracks")

if not (args.artists or args.albums or args.tracks):
    tracks_grouped_artist = group_tracks_artist(tracks)
    tracks_grouped_artist = reorder_groups(tracks_grouped_artist, "artists")
    tracks = degroup_tracks(tracks_grouped_artist)

    tracks_grouped_album = group_tracks_album(tracks)
    tracks_grouped_album = reorder_groups(tracks_grouped_album, "albums")
    tracks = degroup_tracks(tracks_grouped_album)

    tracks = reorder_groups(tracks, "tracks")


number = 0
for index, (unsorted_track, track) in enumerate(zip(reversed(unsorted_tracks), reversed(tracks))):
    if unsorted_track != track:
        number = index
        break


if tracks != unsorted_tracks:
    print("Sorting liked songs")
    unsorted_track_uris = get_uris(unsorted_tracks[0:-number])
    remove_tracks(unsorted_track_uris)
    
    track_uris = get_uris(tracks[0:-number])
    track_uris.reverse()
    add_tracks(track_uris)
else:
    print("Tracks unchanged")

