from flask import Flask, request, redirect, render_template, url_for, session, send_file, Response
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
from playlist import create_or_update_playlist, get_user_playlists, remove_duplicates
from database import initialize_db, add_selected_songs, get_selected_songs, add_to_playlist_history, get_playlist_history
from export import export_playlist_to_csv
from genres import group_tracks_by_genre, create_genre_playlists
from history import initialize_history_db, save_playlist_history, get_user_history
import os
import csv
import re
from io import StringIO

app = Flask(__name__)
app.secret_key = os.urandom(24)

from dotenv import load_dotenv

# load environment variables from the .env file
# load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))
load_dotenv()

# Spotify API credentials from environment variables
CLIENT_ID = os.getenv("CLIENT_ID") # insert your client_id here if developer
CLIENT_SECRET = os.getenv("CLIENT_SECRET") # insert your client_secret here if developer
REDIRECT_URI = os.getenv("REDIRECT_URI") # insert your own redirecturi from Spotify
SCOPE = "playlist-modify-public playlist-modify-private playlist-read-private"

# initialize database
initialize_db()
initialize_history_db()

# initialize Spotipy OAuth
sp_oauth = SpotifyOAuth(client_id=CLIENT_ID, client_secret=CLIENT_SECRET, redirect_uri=REDIRECT_URI, scope=SCOPE)


@app.route("/")
def home():
    """Render the home page with Spotify login option."""
    auth_url = sp_oauth.get_authorize_url()  # get the spotify login url
    return render_template("index.html", auth_url=auth_url)


@app.route("/callback")
def callback():
    """Handle Spotify login callback and fetch user's playlists."""
    code = request.args.get("code")  # get authorization code from callback
    token_info = sp_oauth.get_access_token(code)  # exchange code for access token
    session["token_info"] = token_info  # store token info in session

    sp = Spotify(auth=token_info["access_token"])  # initialize Spotify client
    playlists = get_user_playlists(sp)  # fetch user's playlists

    return render_template("dashboard.html", playlists=playlists)  # show playlist dropdown


# @app.route("/create", methods=["POST"])
# def create():
#     """Handle playlist creation or update based on user input."""
#     token_info = session.get("token_info")
#     if not token_info:
#         return redirect("/")  # redirect to home if no session token

#     sp = Spotify(auth=token_info["access_token"])  # reinitialize Spotify client
#     playlist_id = request.form["playlist_id"]  # get selected playlist ID from form
#     overwrite = request.form.get("overwrite") == "on"  # check if overwrite is selected

#     # get user's Spotify ID and previously selected songs
#     user_id = sp.me()["id"]
#     selected_songs = get_selected_songs(user_id)

#     # create or update the playlist
#     create_or_update_playlist(sp, user_id, playlist_id, selected_songs, overwrite)

#     return "Playlist updated successfully!"

@app.route("/create", methods=["POST"])
def create():
    """Handle playlist creation or update based on user input."""
    token_info = session.get("token_info")
    if not token_info:
        return redirect("/")  # redirect to home if no session token

    sp = Spotify(auth=token_info["access_token"])  # reinitialize Spotify client
    playlist_id = request.form["playlist_id"]  # get selected playlist ID from form
    overwrite = request.form.get("overwrite") == "on"  # check if overwrite is selected

    # get user's Spotify ID and previously selected songs
    user_id = sp.me()["id"]
    selected_songs = get_selected_songs(user_id)

    # create or update the playlist
    new_playlist = create_or_update_playlist(sp, user_id, playlist_id, selected_songs, overwrite)

    # save the new playlist details to the history database
    if new_playlist:
        save_playlist_history(user_id, new_playlist['name'], new_playlist['id'])

    return "Playlist updated successfully!"


@app.route('/export', methods=['GET', 'POST'])
def export_playlist():
    token_info = session.get("token_info")
    if not token_info:
        return redirect("/")  # Redirect to home if no session token

    sp = Spotify(auth=token_info["access_token"])  # Reinitialize Spotify client

    if request.method == 'GET':
        # Fetch user's playlists for dropdown menu
        playlists = sp.current_user_playlists()["items"]
        return render_template('export.html', playlists=playlists)

    elif request.method == 'POST':
        raw_input = request.form.get('playlist_id')

        # Extract playlist ID if input is a URI or URL
        playlist_id = None
        if re.match(r"spotify:playlist:[a-zA-Z0-9]+", raw_input):
            playlist_id = raw_input.split(":")[-1]  # Extract ID from URI
        elif re.match(r"https://open\.spotify\.com/playlist/[a-zA-Z0-9]+", raw_input):
            playlist_id = raw_input.split("/")[-1].split("?")[0]  # Extract ID from URL
        else:
            playlist_id = raw_input  # Assume it's a raw playlist ID

        # Validate playlist ID
        if not playlist_id:
            return render_template('export.html', error="Invalid Playlist ID or URI.")

        try:
            # Call the export function
            csv_file = f"playlist_{playlist_id}.csv"
            message = export_playlist_to_csv(sp, playlist_id, file_name=csv_file)

            if "successfully" in message:
                return send_file(csv_file, as_attachment=True)
            else:
                return render_template('export.html', error=message)
        except Exception as e:
            return render_template('export.html', error=f"An error occurred: {e}")




# @app.route('/recover_playlist', methods=["GET"])
# def recover_playlist():
#     """Recover a previous playlist based on the playlist ID."""
#     playlist_id = request.args.get("playlist_id")
#     token_info = session.get("token_info")
#     if not token_info:
#         return redirect("/")  # redirect to home if no session token

#     sp = Spotify(auth=token_info["access_token"])  # reinitialize Spotify client
#     user_id = sp.me()["id"]

#     # fetch previous playlist songs from the database
#     playlist_data = get_playlist_history(user_id)
#     previous_playlist = next((p for p in playlist_data if p[1] == playlist_id), None)
    
#     if previous_playlist:
#         song_uris = previous_playlist[3].split(",")
#         # Add these songs back to the selected playlist
#         sp.playlist_add_items(playlist_id, song_uris)
#         return "Playlist recovered successfully!"
#     else:
#         return "Playlist not found!"
# investigate this

@app.route("/remove_duplicates", methods=["POST"])
def remove_duplicates_route():
    """Remove duplicate tracks from a playlist."""
    token_info = session.get("token_info")
    if not token_info:
        return redirect("/")  # redirect to home if no session token

    sp = Spotify(auth=token_info["access_token"])  # reinitialize Spotify client
    user_id = sp.me()["id"]
    playlist_id = request.form["playlist_id"]  # get selected playlist ID from form

    # call the remove_duplicates function
    remove_duplicates(sp, playlist_id)

    return "Duplicate tracks removed from the playlist!"

@app.route('/history', methods=["GET"])
def history():
    """Display playlist history for the authenticated user."""
    token_info = session.get("token_info")
    if not token_info:
        return redirect("/")  # redirect to home if no session token

    sp = Spotify(auth=token_info["access_token"])  # reinitialize Spotify client
    user_id = sp.me()["id"]
    
    playlists = get_playlist_history(user_id)  # retrieve user's playlist history

    return render_template("history.html", playlists=playlists)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 5001)))
