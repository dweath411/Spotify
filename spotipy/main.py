# pip install spotapi

'''
Script Workflow Overview:
The main idea in this script is to do 4 things. 
1. Search through a large playlist in your library (e.g., your Liked Songs)
2. Choose 20 songs weekly from that playlist.
3. Add those 20 random songs to your "Origin Radar" playlist and then clears if you wish to get another origin radar playlist.
4. Save the selected songs to a file to ensure they aren't chosen again.
'''

import spotapi  # import SpotAPI to handle Spotify interactions
from spotapi.client import BaseClient
from playlist import get_playlist_tracks, clear_playlist, create_origin_radar_playlist, add_songs_to_playlist
import json  # for handling JSON data
import os  # for file handling
import random  # for selecting random tracks

# initialize SpotAPI instance to manage Spotify API calls without credentials
sp = BaseClient()

# main function to manage playlist logic
def run_spotify_logic(large_playlist_id):
    """
    Retrieves tracks from a large playlist, selects a subset of unique songs, and
    updates a custom playlist with these songs.
    
    Args:
        large_playlist_id (str): ID of the user's large playlist to pull tracks from
    """
    # retrieve tracks from the large playlist
    large_playlist_tracks = get_playlist_tracks(sp, large_playlist_id)

    # load previously selected songs to avoid duplicates
    try:
        with open('selected_songs.json', 'r') as f:
            selected_songs = json.load(f)
    except FileNotFoundError:
        selected_songs = []  # initialize an empty list if the file doesn't exist

    # filter out tracks that have been previously selected
    track_uris = [track['uri'] for track in large_playlist_tracks if track['uri'] not in selected_songs]

    # check if there are at least 20 unique tracks to add
    if len(track_uris) < 20:
        print("Warning: Fewer than 20 unique songs available; all available songs will be added.")
        new_songs = track_uris
    else:
        # select 20 random songs
        new_songs = random.sample(track_uris, 20)

    # update selected songs list to include new songs
    selected_songs.extend(new_songs)
    with open('selected_songs.json', 'w') as f:
        json.dump(selected_songs, f)  # save updated song list

    # check for the custom playlist ID or create it if it doesn't exist
    if os.path.exists('origin_radar_playlist.txt'):
        with open('origin_radar_playlist.txt', 'r') as f:
            origin_radar_playlist_id = f.read().strip()
    else:
        origin_radar_playlist_id = create_origin_radar_playlist(sp)
        with open('origin_radar_playlist.txt', 'w') as f:
            f.write(origin_radar_playlist_id)

    # clear the playlist and add new songs to it
    clear_playlist(sp, origin_radar_playlist_id)
    add_songs_to_playlist(sp, origin_radar_playlist_id, new_songs)

    print("Playlist updated successfully!")


