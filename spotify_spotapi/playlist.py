from spotapi.http import StdClient
from spotapi.client import BaseClient

# Initialize SpotAPI client
http_client = StdClient()
sp = BaseClient(client=http_client)


# function to retrieve all tracks from a specified playlist
def get_playlist_tracks(sp, playlist_id):
    """
    retrieves tracks from a given playlist.

    args:
        sp (spotapi.client.BaseClient): instance of the spotapi client.
        playlist_id (str): id of the playlist to retrieve tracks from.
        
    returns:
        list: a list of track items from the playlist.
    """
    try:
        # fetch playlist tracks using SpotAPI
        response = sp.playlist.get_items(playlist_id)
        return response['items']  # return the list of track items
    except Exception as e:
        print(f"Error retrieving tracks from playlist {playlist_id}: {e}")
        return []  # return an empty list in case of an error


# function to create a new custom playlist called "origin radar"
def create_origin_radar_playlist(sp, user_id):
    """
    creates a new custom playlist.

    args:
        sp (spotapi.client.BaseClient): instance of the spotapi client.
        user_id (str): the spotify user id.
        
    returns:
        str: id of the newly created playlist.
    """
    try:
        # create a playlist using SpotAPI
        response = sp.playlist.create(
            name="origin radar 2.0",
            description="weekly updated playlist of forgotten songs",
            is_public=False,
            user_id=user_id
        )
        return response['id']  # return the new playlist id
    except Exception as e:
        print(f"Error creating playlist for user {user_id}: {e}")
        return None  # return None if playlist creation fails


# function to clear a playlist by removing all its tracks
def clear_playlist(sp, playlist_id):
    """
    clears all songs from the given playlist.

    args:
        sp (spotapi.client.BaseClient): instance of the spotapi client.
        playlist_id (str): id of the playlist to clear.
    """
    try:
        # clear the playlist using SpotAPI
        sp.playlist.clear_items(playlist_id)
        print(f"Playlist {playlist_id} cleared successfully.")
    except Exception as e:
        print(f"Error clearing playlist {playlist_id}: {e}")


# function to add a list of songs to a playlist
def add_songs_to_playlist(sp, playlist_id, songs):
    """
    adds specified songs to a playlist.

    args:
        sp (spotapi.client.BaseClient): instance of the spotapi client.
        playlist_id (str): id of the playlist to add songs to.
        songs (list): a list of track uris to add.
    """
    try:
        # add items to the playlist using SpotAPI
        sp.playlist.add_items(playlist_id, songs)
        print(f"{len(songs)} songs added to playlist {playlist_id} successfully.")
    except Exception as e:
        print(f"Error adding songs to playlist {playlist_id}: {e}")
