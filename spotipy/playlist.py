# import spotapi  # import SpotAPI

# retrieve all tracks from a specified playlist
def get_playlist_tracks(sp, playlist_id):
    """
    Retrieves the tracks from a given playlist.

    Args:
        sp (spotapi.Client): An instance of the SpotAPI client.
        playlist_id (str): The playlist ID to retrieve tracks from.
        
    Returns:
        list: A list of track items from the playlist.
    """
    return sp.playlist_tracks(playlist_id)['items']  # fetch playlist tracks from SpotAPI

# create a custom playlist 
def create_origin_radar_playlist(sp):
    """
    Creates a custom playlist.

    Args:
        sp (spotapi.Client): An instance of the SpotAPI client.
        
    Returns:
        str: ID of the newly created playlist.
    """
    playlist = sp.create_playlist("Release Radar 2.0", description="Weekly updated playlist.")
    return playlist['id']  # return the new playlist ID

# clear a playlist by removing all its tracks
def clear_playlist(sp, playlist_id):
    """
    Clears all songs from the given playlist.

    Args:
        sp (spotapi.Client): An instance of the SpotAPI client.
        playlist_id (str): The playlist ID to clear.
    """
    sp.clear_playlist(playlist_id)  # remove all tracks from playlist

# add a list of songs to a playlist
def add_songs_to_playlist(sp, playlist_id, songs):
    """
    Adds specified songs to a playlist.

    Args:
        sp (spotapi.Client): An instance of the SpotAPI client.
        playlist_id (str): The playlist ID to add songs to.
        songs (list): A list of track URIs to add.
    """
    sp.add_playlist_tracks(playlist_id, songs)  # add songs to playlist
