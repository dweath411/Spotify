import random
import datetime

def get_user_playlists(sp):
    """
    fetch all playlists for the authenticated user.

    args:
        sp (spotipy.Spotify): the spotify client.

    returns:
        list: a list of user's playlists, or an empty list if none are found.
    """
    try:
        playlists = sp.current_user_playlists()
        print(playlists)  # Debugging: print API response
        if playlists and "items" in playlists:
            return [{"id": p["id"], "name": p["name"]} for p in playlists["items"]]
        else:
            print("No playlists found or API response was invalid.")
            return []
    except Exception as e:
        print(f"Error fetching playlists: {e}")
        return []

def create_or_update_playlist(sp, user_id, large_playlist_id, selected_songs, overwrite=True):
    """
    create or update the 'origin radar' playlist.

    args:
        sp (spotipy.Spotify): the spotify client.
        user_id (str): spotify user id.
        large_playlist_id (str): id of the source playlist.
        selected_songs (list): list of previously selected song uris.
        overwrite (bool): whether to overwrite or create a new playlist.
    """
    # fetch tracks from the large playlist
    tracks = sp.playlist_items(large_playlist_id)["items"]
    track_uris = [t["track"]["uri"] for t in tracks if t["track"]["uri"] not in selected_songs]

    # randomly select 20 unique songs
    new_songs = random.sample(track_uris, min(len(track_uris), 20))

    # determine playlist name
    playlist_name = "Origin Radar 2.0"
    if not overwrite:
        playlist_name += f" - Week of {datetime.now().strftime('%b %d')}"

    # create or get existing playlist
    if overwrite:
        playlists = sp.user_playlists(user_id)
        radar_playlist = next((p for p in playlists["items"] if p["name"] == "Origin Radar 2.0"), None)
        if radar_playlist:
            sp.playlist_replace_items(radar_playlist["id"], new_songs)
            return
    playlist = sp.user_playlist_create(user_id, playlist_name, public=False)
    sp.playlist_add_items(playlist["id"], new_songs)
