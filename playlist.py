import random
from datetime import datetime
from database import add_selected_songs


def get_user_playlists(sp):
    """
    Fetch all playlists for the authenticated user, handling pagination and errors.

    Args:
        sp (spotipy.Spotify): The Spotify client.

    Returns:
        list: A list of user's playlists, or an empty list if none are found.
    """
    try:
        playlists = []
        results = sp.current_user_playlists()  # Fetch first batch of playlists
        print(results)  # Debugging: print API response

        if results and "items" in results:
            playlists.extend(results["items"])
        else:
            print("No playlists found or API response was invalid.")
            return []

        # Handle pagination to fetch remaining playlists
        while results["next"]:
            results = sp.next(results)  # Get the next page
            playlists.extend(results["items"])

        return [{"id": p["id"], "name": p["name"]} for p in playlists]
    except Exception as e:
        print(f"Error fetching playlists: {e}")
        return []


def remove_duplicates(sp, playlist_id):
    """
    Removes duplicate tracks from a playlist by comparing track URIs.

    Args:
        sp (spotipy.Spotify): The Spotify client.
        playlist_id (str): ID of the playlist to clean up.

    Returns:
        None
    """
    # Get all tracks from the playlist
    tracks = sp.playlist_items(playlist_id)["items"]
    track_uris = []
    duplicate_tracks = []

    # Loop through tracks and find duplicates
    for track in tracks:
        track_uri = track['track']['uri']
        if track_uri in track_uris:
            duplicate_tracks.append(track['track']['id'])  # Add duplicate track IDs
        else:
            track_uris.append(track_uri)

    if duplicate_tracks:
        # Remove the duplicate tracks from the playlist
        sp.playlist_remove_all_occurrences_of_items(playlist_id, duplicate_tracks)
        print(f"Removed {len(duplicate_tracks)} duplicate(s) from the playlist.")
    else:
        print("No duplicates found in the playlist.")


def create_or_update_playlist(sp, user_id, large_playlist_id, selected_songs, overwrite=True):
    """
    Create or update the 'Origin Radar' playlist.

    Args:
        sp (spotipy.Spotify): The Spotify client.
        user_id (str): Spotify user ID.
        large_playlist_id (str): ID of the source playlist.
        selected_songs (list): List of previously selected song URIs.
        overwrite (bool): Whether to overwrite or create a new playlist.

    Returns:
        dict: Details of the new or updated playlist.
        list: List of added song URIs.
    """
    # Fetch tracks from the large playlist
    tracks = sp.playlist_items(large_playlist_id)["items"]
    track_uris = [t["track"]["uri"] for t in tracks if t["track"]["uri"] not in selected_songs]

    # Randomly select 20 unique songs
    new_songs = random.sample(track_uris, min(len(track_uris), 20))

    # Determine playlist name
    playlist_name = "Origin Radar 2.0"
    if not overwrite:
        playlist_name += f" - Week of {datetime.now().strftime('%b %d')}"

    # Create or update the playlist
    if overwrite:
        playlists = sp.user_playlists(user_id)
        radar_playlist = next((p for p in playlists["items"] if p["name"] == "Origin Radar 2.0"), None)
        if radar_playlist:
            sp.playlist_replace_items(radar_playlist["id"], new_songs)
            return radar_playlist, new_songs

    playlist = sp.user_playlist_create(user_id, playlist_name, public=False)
    sp.playlist_add_items(playlist["id"], new_songs)
    return playlist, new_songs
