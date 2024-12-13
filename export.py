import csv


def export_playlist_to_csv(sp, playlist_id, file_name="playlist_export.csv"):
    """
    export a playlist's track details to a CSV file.

    args:
        sp (spotipy.Spotify): the spotify client.
        playlist_id (str): id of the playlist to export.
        file_name (str): name of the output CSV file.
    """
    tracks = sp.playlist_items(playlist_id)["items"]
    with open(file_name, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Playlist Name", "Track Name", "Artist Name", "Album Name", "Duration (ms)", "Popularity", "Release Date"])

        for track in tracks:
            track_name = track["track"]["name"]
            artist_name = ", ".join([artist["name"] for artist in track["track"]["artists"]])
            album_name = track["track"]["album"]["name"]
            duration_ms = track["track"]["duration_ms"]
            popularity = track["track"]["popularity"]
            release_date = track["track"]["album"]["release_date"]
            writer.writerow([playlist_id, track_name, artist_name, album_name, duration_ms, popularity, release_date])
    
    print(f"Exported playlist {playlist_id} to {file_name}")
