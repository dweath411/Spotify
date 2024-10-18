import spotipy
# from main import sp # import sp variable 

# function to create origin playlist
def create_origin_radar_playlist(user_id, sp):
    try:
        playlist = sp.user_playlist_create(user_id, 'My Origin Radar', public=False, description='Weekly curated playlist from songs I have saved')
        print(f"Playlist 'My Origin Radar' created with ID {playlist['id']}.")
        return playlist['id']
    except spotipy.SpotifyException as e:
        print(f"Error creating playlist for user {user_id}: as {e}")
        return None
# function to get all tracks from a given playlist
def get_playlist_tracks(playlist_id, sp):
    tracks = [] # list to store all the tracks from the playlist
    results = sp.playlist_tracks(playlist_id) # get batch of tracks from the playlist
    # sp is a variable defined in main.py
    # continue this loop if there are multiple pages (Spotify paginates results)
    while results:
        tracks.extend(results['items']) # add the tracks to the list
        results = sp.next(results) if results['next'] else None # get the batch if available

    return tracks # return the complete list of tracks

# function to clear playlist of all songs by replacing its contents with an empty list
def clear_playlist(playlist_id, sp):
    try:
        sp.playlist_replace_items(playlist_id, []) # clear playlist
        print(f"Playlist {playlist_id} cleared successfully")
    except spotipy.SpotifyException as e:
        print(f"Error clearing playlist {playlist_id}: {e}")

# function to add new songs to a given playlist
def add_songs_to_playlist(playlist_id, song_uris, sp):
    try: 
        sp.playlist_add_items(playlist_id, song_uris) # add the list of song URIs to specified playlist
        print(f"Added {len(song_uris)} songs to playlist {playlist_id}.")
    except spotipy.SpotifyException as e:
        print(f"Error adding songs to playlist {playlist_id}: {e}")