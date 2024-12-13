from collections import defaultdict


def group_tracks_by_genre(sp, large_playlist_id):
    """
    group tracks from a large playlist into categories based on their genres.

    args:
        sp (spotipy.Spotify): the spotify client.
        large_playlist_id (str): id of the large playlist to analyze.

    returns:
        dict: a mapping of genres to track uris.
    """
    tracks = sp.playlist_items(large_playlist_id)["items"]  # fetch playlist tracks
    genre_mapping = defaultdict(list)  # dictionary to map genres to track uris
    fallback_genre = "Unknown"  # fallback category for tracks with no genre data

    for item in tracks:
        track = item["track"]
        if not track or not track.get("artists"):  # skip invalid tracks
            continue
        artist_id = track["artists"][0]["id"]  # get the id of the primary artist
        artist = sp.artist(artist_id)  # fetch artist metadata
        genres = artist.get("genres", [])  # get genres associated with the artist

        if genres:
            for genre in genres:
                genre_mapping[genre].append(track["uri"])  # map track to genre
        else:
            genre_mapping[fallback_genre].append(track["uri"])  # handle tracks with no genre data

    return genre_mapping


def create_genre_playlists(sp, user_id, genre_mapping):
    """
    create playlists for each genre using the grouped tracks.

    args:
        sp (spotipy.Spotify): the spotify client.
        user_id (str): the spotify user id.
        genre_mapping (dict): mapping of genres to track uris.

    returns:
        dict: a mapping of genres to created playlist ids.
    """
    playlist_ids = {}  # store playlist ids for each genre
    for genre, uris in genre_mapping.items():
        playlist_name = f"{genre.capitalize()} Mix"
        print(f"Creating playlist: {playlist_name} with {len(uris)} tracks")  # log creation
        playlist = sp.user_playlist_create(user_id, playlist_name, public=False)
        sp.playlist_add_items(playlist["id"], uris[:50])  # limit to 50 tracks per playlist
        playlist_ids[genre] = playlist["id"]

    return playlist_ids
