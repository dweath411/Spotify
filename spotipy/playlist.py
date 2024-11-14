from main import sp # import sp variable 

# function to create origin playlist
def create_origin_radar_playlist(sp):
    """Create a new custom playlist using SpotAPI."""
    playlist = sp.create_playlist('My Origin Radar', public=False, description='Weekly curated playlist from songs I have saved')
    print(f"Playlist 'My Origin Radar' created with ID {playlist['id']}.")
    return playlist['id']

# function to get all tracks from a given playlist
def get_playlist_tracks(sp, playlist_id):
    """Retrieve tracks from a specified playlist using SpotAPI."""
    return sp.playlist_tracks(playlist_id)['items']

# function to clear playlist of all songs by replacing its contents with an empty list
def clear_playlist(sp, playlist_id):
    """Create an existing playlist of all its songs."""
    sp.clear_playlist(playlist_id) # clear playlist
    print(f"Playlist {playlist_id} cleared successfully")

# function to add new songs to a given playlist
def add_songs_to_playlist(playlist_id, songs):
    """Add a list of songs to a playlist"""
    sp.add_playlist_tracks(playlist_id, songs) # add the list of songs to specified playlist
    print(f"Added {len(songs)} songs to playlist {playlist_id}.")
