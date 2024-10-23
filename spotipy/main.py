# pip install spotapi
import spotapi # secondary spotify tool that doesn't require spotify api tokens
import random
import json
import os
from playlist import get_playlist_tracks, clear_playlist, create_origin_radar_playlist, add_songs_to_playlist
# import functions from playlist.py
'''
Prerequisites to using this web application:
1. Spotify Developer Account. Setup your Spotify Developer Account here: https://developer.spotify.com/dashboard/applications
2. Spotify API Authorization: Obtain OAuth tokens using your client ID to interact with Spotify's API. Otherwise, you do not have the permissions!
3. Follow this Authorization Guide to authenticate your requests: https://developer.spotify.com/documentation/general/guides/authorization-guide/
'''

'''
Script Workflow Overview:
The main idea in this script is to do 4 things. 
1. Search through a large playlist in your library (e.g., your Liked Songs)
2. Choose 20 songs weekly from that playlist.
3. Add those 20 random songs to your "Origin Radar" playlist and then clears if you wish to get another origin radar playlist.
4. Save the selected songs to a file to ensure they aren't chosen again.
'''

# Authenticate with the Spotify API. You need to set up authentication using OAuth.
# This involves creating a Spotify App on their developer dashboard.
# You will receive your 'client_id', 'client_secret'.
# Documentation for these parameters are on Spotify's Developer website.


# core function to handle Spotify playlist logic
def run_spotify_logic(large_playlist_id):
    '''
    run_spotify_logic(): Core logic to interact with Spotify API, handles the playlist manipulation.
    This function interacts with SpotAPI to retrieve and modify a Spotify playlist.
    It:
    1. Fetches a large playlist.
    2. Randomly selects new songs from it, avoiding duplicates.
    3. Updates a curated playlist with these songs.
    '''
    # authenticate SpotAPI (authentication using cookies)
    sp =  spotapi.API()
    # input large_playlist_id from user input
    large_playlist_tracks = get_playlist_tracks(sp, large_playlist_id)
    # load previously selected songs to avoid duplication
    try:
        with open('selected_songs.json', 'r') as f:
            selected_songs = json.load(f) # load list of previously selected songs
    except FileNotFoundError:
        selected_songs = [] # if no file is found, start with an empty list

    # get the list of song URIs from the large playlist, excluding those that
    track_uris = [track['track']['uri'] for track in large_playlist_tracks if track['track']['uri'] not in selected_songs]

    # use a set to remove duplicate URIs (in case there are duplicates in the large playlist)
    track_uris = list(set(track_uris)) # convert set back into a list
    # add a case where there are not 20 unique songs to choose from
    if len(track_uris) < 20:
        print(f"Warning: Only {len(track_uris)} unique songs are available. All will be added to the playlist, but try adding some more music in your large playlist for the full experience!")
    # randomly select 20 unique songs from the remaining track URIs
        new_songs = track_uris # add all available songs
    else:
        new_songs = random.sample(track_uris, 20) # randomly pick 20

    # update the selected song list 
    selected_songs.extend(new_songs)

    # save the updated selected songs list to avoid duplicates
    with open('selected_songs.json', 'w') as f:
        json.dump(selected_songs, f)

    # check if the playlist has already been created, looking for the saved playlist ID
    if os.path.exists('origin_radar_playlist.txt'):
        # load playlist ID from the file
        with open('origin_radar_playlist.txt', 'r') as f:
            origin_radar_playlist_id = f.read().strip() # get existing playlist ID
            print(f"Using existing playlist ID: {origin_radar_playlist_id}")
    else:
        # if no playlist ID exists, create a new playlist
        origin_radar_playlist_id = create_origin_radar_playlist(sp)
        if origin_radar_playlist_id: # check if playlist creation was a success
        # save the  playlist ID to a file, for future reference
            with open('origin_radar_playlist_id.txt', 'w') as f:
                f.write(origin_radar_playlist_id)
            print(f"Created new playlist with ID: {origin_radar_playlist_id} and saved it.")
        else:
            print("Failed to create a new playlist. Exiting")
            exit(1) # exit the script if playlist creation fails
    
    # clear the playlist before adding new songs
    clear_playlist(sp, origin_radar_playlist_id)

    # add new songs to the playlist
    add_songs_to_playlist(sp, origin_radar_playlist_id, new_songs) 

    return "Playlist updated with new songs!"

