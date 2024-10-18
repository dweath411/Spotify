# pip install spotipy # install spotipy if not already installed
# make sure your python interpreter is correct
# if spotipy issues persist, https://stackoverflow.com/questions/67116146/vscode-no-module-named-spotipy
import spotipy # import spotipy, our main library
from spotipy.oauth2 import SpotifyOAuth
# import spotapi # secondary spotify tool that doesn't require spotify api tokens
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


# main function to run Spotify logic
def run_spotify_logic(client_id, client_secret, large_playlist_id):
    '''
    run_spotify_logic(): Core logic to interact with Spotify API, handles the playlist manipulation:
    Authenticates the user using credentials (client_id, client_secret).
    Retrieves tracks from the user's large playlist and filters out already selected songs.
    Randomly picks 20 new songs and saves them to ensure no duplicates are chosen next time.
    If the playlist doesn't exist, it creates one and adds the new songs; if it exists, it clears and refills it weekly.
    '''
    redirect_uri =  "http://localhost:5001/callback"  # set the redirect URI for Spotify OAuth
    sp =  spotipy.Spotify(auth_manager = SpotifyOAuth(
        client_id = client_id, # your Spotify client ID
        client_secret = client_secret, # your Spotify client secret
        redirect_uri = redirect_uri, # redirect URI for OAuth callback
        scope="playlist-modify-public playlist-modify-private playlist-read-private"  # permissions to manage playlists
    ))
    # input large_playlist_id from user input
    large_playlist_tracks = get_playlist_tracks(large_playlist_id, sp)
    user_id = sp.current_user()['id'] # get the authenticated user's Spotify ID
   
    # randomly select 20 songs from this playlist, while also ensuring they haven't been selected before
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
        new_songs = random.sample(track_uris, 20)

    # update the selected song list 
    selected_songs.extend(new_songs)

    # save the updated selected songs list to avoid duplicates
    with open('selected_songs.json', 'w') as f:
        json.dump(selected_songs, f)

    # get user ID for creating playlist
    user_id = sp.me()['id'] 

    # check if the playlist has already been created, looking for the saved playlist ID
    if os.path.exists('origin_radar_playlist.txt'):
        # load playlist ID from the file
        with open('origin_radar_playlist.txt', 'r') as f:
            origin_radar_playlist_id = f.read().strip()
            print(f"Using existing playlist ID: {origin_radar_playlist_id}")
    else:
        # if no playlist ID exists, create a new playlist
        origin_radar_playlist_id = create_origin_radar_playlist(user_id)
        if origin_radar_playlist_id: # check if playlist creation was a success
        # save the  playlist ID to a file, for future reference
            with open('origin_radar_playlist_id.txt', 'w') as f:
                f.write(origin_radar_playlist_id)
            print(f"Created new playlist with ID: {origin_radar_playlist_id} and saved it.")
        else:
            print("Failed to create a new playlist. Exiting")
            exit(1) # exit the script if playlist creation fails
    # clear the playlist before adding new songs
    clear_playlist(origin_radar_playlist_id, sp)

    # add new songs to the playlist
    add_songs_to_playlist(origin_radar_playlist_id, new_songs, sp) 

    return "Playlist updated with new songs!"

