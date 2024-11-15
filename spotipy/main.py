'''
Script Workflow Overview:
The main idea in this script is to do 4 things. 
1. Search through a large playlist in your library (e.g., your Liked Songs)
2. Choose 20 songs weekly from that playlist.
3. Add those 20 random songs to your "Origin Radar" playlist and then clears if you wish to get another origin radar playlist.
4. Save the selected songs to a file to ensure they aren't chosen again.
'''


import spotapi
import json
import random
import os
from playlist import get_playlist_tracks, clear_playlist, add_songs_to_playlist, create_origin_radar_playlist
# import functions from playlist.py

# initialize the SpotAPI client
sp = spotapi.Client()

# function to create or update the playlist
def create_or_update_playlist(user_id, large_playlist_id):
    """
    main function to update the origin radar playlist weekly.
    
    args:
        user_id (str): spotify user id for personalized json storage.
        large_playlist_id (str): id of the large playlist to draw from.
    """
    # load user-specific json file to track previously selected songs
    user_file = f"{user_id}_selected_songs.json"
    try:
        with open(user_file, 'r') as f:
            selected_songs = json.load(f)
    except FileNotFoundError:
        selected_songs = []  # start with an empty list if no file exists

    # fetch tracks from the large playlist
    large_playlist_tracks = get_playlist_tracks(sp, large_playlist_id)
    track_uris = [track['uri'] for track in large_playlist_tracks if track['uri'] not in selected_songs]

    # select 20 unique songs
    if len(track_uris) < 20:
        print("warning: fewer than 20 unique songs available.")
        new_songs = track_uris
    else:
        new_songs = random.sample(track_uris, 20)
    
    # save selected songs to a user-specific file
    selected_songs.extend(new_songs)
    with open(user_file, 'w') as f:
        json.dump(selected_songs, f)

    # check if "origin radar" exists, create if not
    playlist_id_file = f"{user_id}_origin_radar_playlist.txt"
    if os.path.exists(playlist_id_file):
        with open(playlist_id_file, 'r') as f:
            origin_radar_playlist_id = f.read().strip()
    else:
        origin_radar_playlist_id = create_origin_radar_playlist(sp, user_id)
        with open(playlist_id_file, 'w') as f:
            f.write(origin_radar_playlist_id)
    
    # clear the existing playlist before adding new songs
    clear_playlist(sp, origin_radar_playlist_id)
    add_songs_to_playlist(sp, origin_radar_playlist_id, new_songs)

    print("playlist updated successfully!")


