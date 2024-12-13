def remove_duplicates(sp, playlist_id):
    """
    remove duplicate tracks from a playlist.

    args:
        sp (spotipy.Spotify): the spotify client.
        playlist_id (str): id of the playlist to clean.
    """
    tracks = sp.playlist_items(playlist_id)["items"]
    track_uris = [track["track"]["uri"] for track in tracks]

    # identify duplicates by counting occurrences of track URIs
    unique_uris = list(set(track_uris))
    duplicates = [uri for uri in track_uris if track_uris.count(uri) > 1]

    # remove duplicates from playlist
    for duplicate in duplicates:
        tracks_to_remove = [track["track"]["id"] for track in tracks if track["track"]["uri"] == duplicate]
        sp.playlist_remove_all_occurrences_of_items(playlist_id, tracks_to_remove)
    print(f"Removed {len(duplicates)} duplicate tracks.")
