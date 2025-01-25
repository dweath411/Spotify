import random
from datetime import datetime 
from database import add_selected_songs 
import csv  # used for writing data to CSV files
from spotipy import Spotify  # spotify client library
import os 

def get_user_playlists(sp):
    """
    fetch all playlists for the authenticated user, handling pagination and errors.

    args:
        sp (spotipy.Spotify): the spotify client.

    returns:
        list: a list of user's playlists, or an empty list if none are found.
    """
    try:
        playlists = []  # initialize an empty list to store playlists
        results = sp.current_user_playlists()  # fetch the first batch of playlists
        print(results)  # debugging: print API response to console

        if results and "items" in results:  # check if playlists exist in the response
            playlists.extend(results["items"])  # add fetched playlists to the list
        else:
            print("No playlists found or API response was invalid.")  # log an error message
            return []  # return an empty list if no playlists are found

        # handle pagination to fetch remaining playlists
        while results["next"]:  # continue until no next page is available
            results = sp.next(results)  # fetch the next page
            playlists.extend(results["items"])  # add fetched playlists to the list

        # return a simplified list of playlists with their ids and names
        return [{"id": p["id"], "name": p["name"]} for p in playlists]
    except Exception as e:
        print(f"Error fetching playlists: {e}")  # log the error
        return []  # return an empty list in case of an error

def remove_duplicates(sp, playlist_id):
    """
    removes duplicate tracks from a playlist by comparing track uris.

    args:
        sp (spotipy.Spotify): the spotify client.
        playlist_id (str): id of the playlist to clean up.

    returns:
        none
    """
    # get all tracks from the playlist
    tracks = sp.playlist_items(playlist_id)["items"]  # fetch playlist tracks
    track_uris = []  # list to store unique track URIs
    duplicate_tracks = []  # list to store duplicate track IDs

    # loop through tracks and find duplicates
    for track in tracks:
        track_uri = track['track']['uri']  # get the track URI
        if track_uri in track_uris:  # check if the URI already exists in the list
            duplicate_tracks.append(track['track']['id'])  # add the track ID to duplicates
        else:
            track_uris.append(track_uri)  # add unique URIs to the list

    if duplicate_tracks:  # check if duplicates were found
        # remove the duplicate tracks from the playlist
        sp.playlist_remove_all_occurrences_of_items(playlist_id, duplicate_tracks)
        print(f"Removed {len(duplicate_tracks)} duplicate(s) from the playlist.")  # log the number of removed duplicates
    else:
        print("No duplicates found in the playlist.")  # log if no duplicates are found

def create_or_update_playlist(sp, user_id, large_playlist_id, selected_songs, overwrite=True):
    """
    create or update the 'origin radar' playlist.

    args:
        sp (spotipy.Spotify): the spotify client.
        user_id (str): spotify user id.
        large_playlist_id (str): id of the source playlist.
        selected_songs (list): list of previously selected song uris.
        overwrite (bool): whether to overwrite or create a new playlist.

    returns:
        dict: details of the new or updated playlist.
        list: list of added song uris.
    """
    # fetch tracks from the large playlist
    tracks = sp.playlist_items(large_playlist_id)["items"]  # get all tracks from the source playlist
    # filter out tracks already in selected_songs and get their URIs
    track_uris = [t["track"]["uri"] for t in tracks if t["track"]["uri"] not in selected_songs]

    # randomly select 20 unique songs from the available tracks
    new_songs = random.sample(track_uris, min(len(track_uris), 20))

    # determine the name of the new or updated playlist
    playlist_name = "Origin Radar 2.0"
    if not overwrite:  # add a date suffix if not overwriting
        playlist_name += f" - Week of {datetime.now().strftime('%b %d')}"

    # create or update the playlist
    if overwrite:
        playlists = sp.user_playlists(user_id)  # fetch all playlists for the user
        # find an existing playlist named 'Origin Radar 2.0'
        radar_playlist = next((p for p in playlists["items"] if p["name"] == "Origin Radar 2.0"), None)
        if radar_playlist:  # if the playlist exists, replace its tracks
            sp.playlist_replace_items(radar_playlist["id"], new_songs)
            return radar_playlist, new_songs  # return updated playlist details and new songs

    # create a new playlist if overwriting is not enabled or no existing playlist was found
    playlist = sp.user_playlist_create(user_id, playlist_name, public=False)
    sp.playlist_add_items(playlist["id"], new_songs)  # add new tracks to the playlist
    return playlist, new_songs  # return new playlist details and added songs

def export_playlist_to_csv(sp, playlist_id, playlist_name, file_name="playlist_export.csv"):
    """
    export a playlist's track details to a csv file.

    args:
        sp (spotipy.Spotify): the spotify client.
        playlist_id (str): id of the playlist to export.
        playlist_name (str): user-input name of the playlist.
        file_name (str): name of the output csv file.
    """
    try:
        # initialize an empty list to hold tracks
        all_tracks = []
        # fetch the first batch of tracks
        results = sp.playlist_items(playlist_id)
        all_tracks.extend(results['items'])

        # handle pagination to fetch remaining tracks
        while results['next']:
            results = sp.next(results)  # fetch the next page of tracks
            all_tracks.extend(results['items'])

    except Exception as e:
        print(f"Error fetching playlist items: {e}")  # log any errors
        return "Error fetching playlist data."

    # check if there are tracks to export
    if not all_tracks:
        print("No tracks found in playlist.")  # log if the playlist is empty
        return "No tracks found to export."

    try:
        # open a CSV file to write the data
        with open(file_name, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)  # initialize CSV writer
            # write the header row
            writer.writerow(["Playlist ID", "Playlist Name", "Track Name", "Artist Name", "Album Name", "Duration (s)", "Popularity", "Release Date"])

            # write track details row by row
            for track in all_tracks:
                track_name = track["track"]["name"]  # get track name
                artist_name = ", ".join([artist["name"] for artist in track["track"]["artists"]])  # get all artist names
                album_name = track["track"]["album"]["name"]  # get album name
                duration_s = track["track"]["duration_ms"] // 1000  # convert duration from milliseconds to seconds
                popularity = track["track"]["popularity"]  # get track popularity
                release_date = track["track"]["album"]["release_date"]  # get release date

                # write the track details to the CSV file
                writer.writerow([playlist_id, playlist_name, track_name, artist_name, album_name, duration_s, popularity, release_date])

        print(f"Exported playlist {playlist_name} ({playlist_id}) to {file_name}")  # log success message
        return f"Playlist {playlist_name} exported successfully."

    except Exception as e:
        print(f"Error writing to CSV: {e}")  # log errors while writing to the file
        return "Error saving CSV file."

def get_tracks_from_playlist(sp, playlist_id):
    """
    fetch tracks from a user-selected playlist.

    args:
        sp (spotipy.Spotify): the spotify client.
        playlist_id (str): id of the playlist to fetch tracks from.

    returns:
        list: a list of track uris from the playlist.
    """
    def get_tracks_from_playlist(sp, playlist_id):
        try:
            all_tracks = []  # list to store all track items
            results = sp.playlist_items(playlist_id)  # fetch the first batch of tracks
            print(f"Results type: {type(results)}")  # check type of results
            print(f"Results content: {results}")  # log the full results

            while results:
                all_tracks.extend(results["items"])  # append tracks from current batch
                results = sp.next(results) if results["next"] else None  # fetch next page if available

            track_uris = [item["track"]["uri"] for item in all_tracks if item["track"]]
            print(f"Track URIs: {track_uris}")  # log the extracted track URIs
            return track_uris
        except Exception as e:
            print(f"Error fetching tracks from playlist: {e}")  # log the error
            return []
    # logging added to the above version
    # try:
    #     all_tracks = []  # list to store all track items
    #     results = sp.playlist_items(playlist_id)  # fetch the first batch of tracks

    #     # iterate through results to handle pagination
    #     while results:
    #         all_tracks.extend(results["items"])  # append tracks from current batch
    #         results = sp.next(results) if results["next"] else None  # fetch next page if available

    #     # extract uris for tracks that are valid
    #     track_uris = [item["track"]["uri"] for item in all_tracks if item["track"]]
    #     return track_uris  # return the list of track uris

    # except Exception as e:
    #     print(f"Error fetching tracks from playlist: {e}")  # log the error
    #     return []




# function callable by the following command ->
# export_playlist_to_csv(sp, "4oeP3PbakXBlj8tPh3nEPx", "My Playlist")

