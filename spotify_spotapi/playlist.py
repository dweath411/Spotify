# function to retrieve all tracks from a specified playlist
def get_playlist_tracks(sp, playlist_id):
    """
    retrieves tracks from a given playlist.

    args:
        sp (spotapi.client): instance of the spotapi client.
        playlist_id (str): id of the playlist to retrieve tracks from.
        
    returns:
        list: a list of track items from the playlist.
    """
    return sp.playlist_tracks(playlist_id)['items']  # fetch playlist tracks

# function to create a new custom playlist called "origin radar"
def create_origin_radar_playlist(sp, user_id):
    """
    creates a new custom playlist.

    args:
        sp (spotapi.client): instance of the spotapi client.
        user_id (str): the spotify user id.
        
    returns:
        str: id of the newly created playlist.
    """
    playlist = sp.create_playlist("origin radar 2.0", user_id, description="weekly updated playlist of forgotten songs")
    return playlist['id']  # return the new playlist id

# function to clear a playlist by removing all its tracks
def clear_playlist(sp, playlist_id):
    """
    clears all songs from the given playlist.

    args:
        sp (spotapi.client): instance of the spotapi client.
        playlist_id (str): id of the playlist to clear.
    """
    sp.clear_playlist(playlist_id)  # remove all tracks from the playlist

# function to add a list of songs to a playlist
def add_songs_to_playlist(sp, playlist_id, songs):
    """
    adds specified songs to a playlist.

    args:
        sp (spotapi.client): instance of the spotapi client.
        playlist_id (str): id of the playlist to add songs to.
        songs (list): a list of track uris to add.
    """
    sp.add_playlist_tracks(playlist_id, songs)  # add songs to the playlist
