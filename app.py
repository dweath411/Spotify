from flask import Flask, request, redirect, render_template, url_for, session, send_file, Response
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
from playlist import create_or_update_playlist, get_user_playlists, remove_duplicates
from database import initialize_db, add_selected_songs, get_selected_songs
from export import export_playlist_to_csv
import os
from analysis import fetch_top_tracks, generate_analysis_plot
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
SCOPE = "user-top-read playlist-modify-public playlist-modify-private playlist-read-private"

# initialize database
initialize_db()

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


@app.route("/create", methods=["POST"])
def create():
    """Handle playlist creation or update based on user input."""
    token_info = session.get("token_info")
    if not token_info:
        return redirect("/")  # redirect to home if no session token

    # refresh the token if it's expired
    if sp_oauth.is_token_expired(token_info):
        token_info = sp_oauth.refresh_access_token(token_info["refresh_token"])
        session["token_info"] = token_info

    sp = Spotify(auth=token_info["access_token"])  # reinitialize Spotify client
    playlist_id = request.form["playlist_id"]  # get selected playlist ID from form
    overwrite = request.form.get("overwrite") == "on"  # check if overwrite is selected

    # get user's Spotify ID and previously selected songs
    user_id = sp.me()["id"]
    selected_songs = get_selected_songs(user_id)

    # create or update the playlist
    new_playlist, new_songs = create_or_update_playlist(sp, user_id, playlist_id, selected_songs, overwrite)

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


@app.route("/song_analysis/<time_range>")
def song_analysis(time_range):
    """Display top songs analysis for the selected time range."""
    token_info = session.get("token_info")
    if not token_info:
        return redirect("/")

    sp = Spotify(auth=token_info["access_token"])
    tracks = fetch_top_tracks(sp, time_range=time_range)

    if not tracks:
        return "No tracks found for this time range."

    plot_data = generate_analysis_plot(tracks, time_range)
    return render_template("song_analysis.html", plot_data=plot_data, time_range=time_range)

@app.route("/remove_duplicates", methods=["POST"])
def remove_duplicates_route():
    """Remove duplicate tracks from a playlist."""
    token_info = session.get("token_info")
    if not token_info:
        return redirect("/")  # redirect to home if no session token

    sp = Spotify(auth=token_info["access_token"])  # reinitialize Spotify client
    playlist_id = request.form.get("playlist_id")  # get selected playlist ID from form

    if not playlist_id:
        return "Playlist ID is missing.", 400

    remove_duplicates(sp, playlist_id)

    return "Duplicate tracks removed from the playlist!"


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 5001)))
