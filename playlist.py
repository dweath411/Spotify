import random
from datetime import datetime
from database import add_selected_songs
import csv
from spotipy import Spotify
import os


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
        results = sp.current_user_playlists()  # fetch first batch of playlists
        print(results)  # debugging: print API response

        if results and "items" in results:
            playlists.extend(results["items"])
        else:
            print("No playlists found or API response was invalid.")
            return []

        # handle pagination to fetch remaining playlists
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
    # get all tracks from the playlist
    tracks = sp.playlist_items(playlist_id)["items"]
    track_uris = []
    duplicate_tracks = []

    # loop through tracks and find duplicates
    for track in tracks:
        track_uri = track['track']['uri']
        if track_uri in track_uris:
            duplicate_tracks.append(track['track']['id'])  # add duplicate track IDs
        else:
            track_uris.append(track_uri)

    if duplicate_tracks:
        # remove the duplicate tracks from the playlist
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
    # fetch tracks from the large playlist
    tracks = sp.playlist_items(large_playlist_id)["items"]
    track_uris = [t["track"]["uri"] for t in tracks if t["track"]["uri"] not in selected_songs]

    # randomly select 20 unique songs
    new_songs = random.sample(track_uris, min(len(track_uris), 20))

    # determine playlist name
    playlist_name = "Origin Radar 2.0"
    if not overwrite:
        playlist_name += f" - Week of {datetime.now().strftime('%b %d')}"

    # create or update the playlist
    if overwrite:
        playlists = sp.user_playlists(user_id)
        radar_playlist = next((p for p in playlists["items"] if p["name"] == "Origin Radar 2.0"), None)
        if radar_playlist:
            sp.playlist_replace_items(radar_playlist["id"], new_songs)
            return radar_playlist, new_songs

    playlist = sp.user_playlist_create(user_id, playlist_name, public=False)
    sp.playlist_add_items(playlist["id"], new_songs)
    return playlist, new_songs

def export_playlist_to_csv(sp, playlist_id, playlist_name, file_name="playlist_export.csv"):
    """
    Export a playlist's track details to a CSV file.

    Args:
        sp (spotipy.Spotify): the Spotify client.
        playlist_id (str): ID of the playlist to export.
        playlist_name (str): User-input name of the playlist.
        file_name (str): Name of the output CSV file.
    """
    try:
        # initialize empty list to hold tracks
        all_tracks = []
        # initial request to get first batch of tracks
        results = sp.playlist_items(playlist_id)
        all_tracks.extend(results['items'])

        # handle pagination if more than 100 tracks exist
        while results['next']:
            results = sp.next(results)
            all_tracks.extend(results['items'])
        
    except Exception as e:
        print(f"Error fetching playlist items: {e}")
        return "Error fetching playlist data."

    # check if we have tracks to export
    if not all_tracks:
        print("No tracks found in playlist.")
        return "No tracks found to export."

    try:
        # open a CSV file to write the data
        with open(file_name, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            # write header with additional Playlist Name column
            writer.writerow(["Playlist ID", "Playlist Name", "Track Name", "Artist Name", "Album Name", "Duration (s)", "Popularity", "Release Date"])

            for track in all_tracks:
                track_name = track["track"]["name"]
                artist_name = ", ".join([artist["name"] for artist in track["track"]["artists"]])
                album_name = track["track"]["album"]["name"]
                duration_s = track["track"]["duration_ms"] // 1000  # Convert ms to seconds
                popularity = track["track"]["popularity"]
                release_date = track["track"]["album"]["release_date"]

                # write the data for this track into the CSV file
                writer.writerow([playlist_id, playlist_name, track_name, artist_name, album_name, duration_s, popularity, release_date])

        print(f"Exported playlist {playlist_name} ({playlist_id}) to {file_name}")
        return f"Playlist {playlist_name} exported successfully."

    except Exception as e:
        print(f"Error writing to CSV: {e}")
        return "Error saving CSV file."

# function callable by the following command ->
# export_playlist_to_csv(sp, "4oeP3PbakXBlj8tPh3nEPx", "My Playlist")
