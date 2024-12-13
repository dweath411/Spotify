import csv
from spotipy import Spotify
import os

def export_playlist_to_csv(sp, playlist_id, file_name="playlist_export.csv"):
    """
    Export a playlist's track details to a CSV file.

    Args:
        sp (spotipy.Spotify): the Spotify client.
        playlist_id (str): ID of the playlist to export.
        file_name (str): Name of the output CSV file.
    """
    try:
        # Initialize empty list to hold tracks
        all_tracks = []
        # Initial request to get first batch of tracks
        results = sp.playlist_items(playlist_id)
        all_tracks.extend(results['items'])

        # Handle pagination if more than 100 tracks exist
        while results['next']:
            results = sp.next(results)
            all_tracks.extend(results['items'])
        
    except Exception as e:
        print(f"Error fetching playlist items: {e}")
        return "Error fetching playlist data."

    # Check if we have tracks to export
    if not all_tracks:
        print("No tracks found in playlist.")
        return "No tracks found to export."

    try:
        # Open a CSV file to write the data
        with open(file_name, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["Playlist Name", "Track Name", "Artist Name", "Album Name", "Duration (ms)", "Popularity", "Release Date"])

            for track in all_tracks:
                track_name = track["track"]["name"]
                artist_name = ", ".join([artist["name"] for artist in track["track"]["artists"]])
                album_name = track["track"]["album"]["name"]
                duration_ms = track["track"]["duration_ms"]
                popularity = track["track"]["popularity"]
                release_date = track["track"]["album"]["release_date"]

                # Write the data for this track into the CSV file
                writer.writerow([playlist_id, track_name, artist_name, album_name, duration_ms, popularity, release_date])

        print(f"Exported playlist {playlist_id} to {file_name}")
        return f"Playlist {playlist_id} exported successfully."

    except Exception as e:
        print(f"Error writing to CSV: {e}")
        return "Error saving CSV file."
