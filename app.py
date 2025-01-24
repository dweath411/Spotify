from flask import Flask, request, redirect, render_template, url_for, session, send_file, Response
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
from playlist import create_or_update_playlist, get_user_playlists, remove_duplicates, export_playlist_to_csv, get_tracks_from_playlist
from database import initialize_db, add_selected_songs, get_selected_songs
import os 
from analysis import fetch_top_tracks, generate_analysis_plot
import csv  # module for csv file handling
import base64  # module for encoding/decoding binary data to/from base64
import re  # regex library for pattern matching
import io  # handles input/output streams
import matplotlib
# matplotlib.use("Agg")  # use agg backend (remove when deploying to render)
# matplotlib for plotting; ensure correct backend for production
import matplotlib.pyplot as plt
from io import StringIO, BytesIO  # used for in-memory streams

# flask application instance
app = Flask(__name__)

# set a secret key 
app.secret_key = os.urandom(24)

from dotenv import load_dotenv
# load environment variables from .env file only in local development
if os.getenv("RENDER") is None:  # check if the app is not running on Render
    load_dotenv()

# spotify api credentials retrieved from environment variables
CLIENT_ID = os.getenv("CLIENT_ID")  # spotify client id
CLIENT_SECRET = os.getenv("CLIENT_SECRET")  # spotify client secret
SCOPE = os.getenv("SCOPE")  # spotify scope for permissions
SPOTIFY_REDIRECT_URI = os.getenv("SPOTIPY_REDIRECT_URI") or os.getenv("REDIRECT_URI")
# fallback to alternate variable if SPOTIPY_REDIRECT_URI is not set

if not SPOTIFY_REDIRECT_URI:
    raise ValueError("REDIRECT_URI is not set in environment variables.")
# ensure redirect uri is correctly defined

# initialize the database
initialize_db()

# initialize spotipy oauth for spotify authentication
sp_oauth = SpotifyOAuth(client_id=CLIENT_ID, client_secret=CLIENT_SECRET, redirect_uri=SPOTIFY_REDIRECT_URI, scope=SCOPE)

@app.route("/")
def home():
    """render the home page with spotify login option."""
    auth_url = sp_oauth.get_authorize_url()  # generate spotify login url
    return render_template("index.html", auth_url=auth_url)  # pass url to template

@app.route("/callback")
def callback():
    """handle spotify oauth callback."""
    print("Callback route accessed.")  # log access
    code = request.args.get("code")  # retrieve authorization code
    error = request.args.get("error")  # retrieve error message, if any

    if error:
        return f"Error during authentication: {error}", 400  # handle auth errors

    if not code:
        return "No authorization code provided by Spotify.", 400  # handle missing code

    try:
        # exchange code for access token and store in session
        token_info = sp_oauth.get_access_token(code)
        session["token_info"] = token_info

        # ensure token is valid or refreshed
        token_info = refresh_token()
        sp = Spotify(auth=token_info["access_token"])  # reinitialize spotify client

        # fetch user's playlists and render dashboard
        playlists = get_user_playlists(sp)
        return render_template("dashboard.html", playlists=playlists)

    except Exception as e:
        print(f"Error in callback: {e}")  # log error
        return f"An error occurred during Spotify authentication: {e}", 500

@app.route("/create", methods=["POST"])
def create():
    """handle playlist creation or update based on user input."""
    token_info = session.get("token_info")
    if not token_info:
        return redirect("/")  # redirect to home if no session token

    # refresh token if expired
    if sp_oauth.is_token_expired(token_info):
        token_info = sp_oauth.refresh_access_token(token_info["refresh_token"])
        session["token_info"] = token_info

    sp = Spotify(auth=token_info["access_token"])  # reinitialize spotify client
    playlist_id = request.form["playlist_id"]  # get selected playlist id
    overwrite = request.form.get("overwrite") == "on"  # check overwrite option

    # retrieve user id and previously selected songs
    user_id = sp.me()["id"]
    selected_songs = get_selected_songs(user_id)

    # create or update the playlist
    new_playlist, new_songs = create_or_update_playlist(sp, user_id, playlist_id, selected_songs, overwrite)

    return "Playlist updated successfully!"  # confirm success

@app.route('/export', methods=['GET', 'POST'])
def export_playlist():
    """export a playlist to csv."""
    token_info = session.get("token_info")
    if not token_info:
        return redirect("/")  # redirect to home if no session token

    sp = Spotify(auth=token_info["access_token"])  # reinitialize spotify client

    if request.method == 'GET':
        playlists = sp.current_user_playlists()["items"]  # fetch playlists
        return render_template('export.html', playlists=playlists)

    elif request.method == 'POST':
        raw_input = request.form.get('playlist_id')
        playlist_id = None
        playlist_name = None

        # extract playlist id from uri or url
        if re.match(r"spotify:playlist:[a-zA-Z0-9]+", raw_input):
            playlist_id = raw_input.split(":")[-1]
        elif re.match(r"https://open\.spotify\.com/playlist/[a-zA-Z0-9]+", raw_input):
            playlist_id = raw_input.split("/")[-1].split("?")[0]
        else:
            playlist_id = raw_input

        if not playlist_id:
            return render_template('export.html', error="Invalid Playlist ID or URI.")

        try:
            playlist = sp.playlist(playlist_id)  # fetch playlist name
            playlist_name = playlist["name"]
        except Exception as e:
            return render_template('export.html', error=f"Error fetching playlist details: {e}")

        try:
            csv_file = f"playlist_{playlist_id}.csv"  # generate csv filename
            message = export_playlist_to_csv(sp, playlist_id, playlist_name, file_name=csv_file)

            if "successfully" in message:
                return send_file(csv_file, as_attachment=True)
            else:
                return render_template('export.html', error=message)
        except Exception as e:
            return render_template('export.html', error=f"An error occurred: {e}")


@app.route('/analysis', methods=['GET'])
def song_analysis():
    time_range = request.args.get('time_range', 'medium_term')  # default to medium_term
    sp = Spotify(auth=session.get("token_info")["access_token"])

    # fetch top tracks
    tracks = fetch_top_tracks(sp, time_range=time_range)

    # prepare data for plotting
    track_names = [track["name"] for track in tracks]
    track_durations = [track["duration_ms"] / 3600000 for track in tracks]  # convert ms to hours

    # generate the plot
    plt.figure(figsize=(10, 6))
    plt.barh(track_names, track_durations, color="#1DB954")
    plt.xlabel("Hours Listened")
    plt.ylabel("Track Name")
    plt.title(f"Top 10 Tracks - {time_range.replace('_', ' ').title()}")
    plt.gca().invert_yaxis()  # invert y-axis for better readability

    # save plot to a bytes buffer
    buffer = io.BytesIO()
    plt.savefig(buffer, format="png")
    buffer.seek(0)
    plt.close()

    # encode plot as base64 string
    plot_data = base64.b64encode(buffer.getvalue()).decode("utf-8")
    print(plot_data[:100])

    return render_template(
        "analysis.html",
        time_range=time_range.replace("_", " ").title(),
        plot_data=plot_data
    )

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

@app.route("/generate_recommendations", methods=["POST"])
def generate_recommendations():
    """
    generate a playlist of recommendations based on a user-selected playlist.
    """
    token_info = session.get("token_info")  # fetch token from session
    if not token_info:
        return redirect("/")  # redirect to home if no session token

    # refresh the token if expired
    if sp_oauth.is_token_expired(token_info):
        token_info = sp_oauth.refresh_access_token(token_info["refresh_token"])
        session["token_info"] = token_info

    try:
        sp = Spotify(auth=token_info["access_token"])  # reinitialize spotify client
        user_id = sp.me()["id"]  # fetch user's spotify id

        # get the user-selected playlist id
        playlist_id = request.form.get("playlist_id")
        if not playlist_id:
            return "No playlist selected for generating recommendations.", 400

        # fetch tracks from the selected playlist
        playlist_tracks = get_tracks_from_playlist(sp, playlist_id)
        if not playlist_tracks:
            return "The selected playlist has no tracks to generate recommendations.", 400

        # get seed tracks for recommendations (limit Spotify's seed to 5 tracks)
        seed_tracks = playlist_tracks[:5]

        # fetch recommendations using Spotify's recommendation API
        recommendations = sp.recommendations(seed_tracks=seed_tracks, limit=20)
        recommended_uris = [track["uri"] for track in recommendations["tracks"]]

        # create a new playlist with recommendations
        playlist_name = "Your Recommendations"
        playlist_description = "A playlist generated based on your selected playlist."
        new_playlist = sp.user_playlist_create(
            user=user_id, name=playlist_name, public=False, description=playlist_description
        )
        sp.playlist_add_items(new_playlist["id"], recommended_uris)  # add recommended songs to the playlist

        return f"Playlist '{playlist_name}' created successfully!", 200

    except Exception as e:
        print(f"Error generating recommendations: {e}")  # log the error
        return f"An error occurred: {e}", 500



def refresh_token():
    """Refresh Spotify token if expired."""
    token_info = session.get("token_info", {})
    if not sp_oauth.is_token_expired(token_info):
        return token_info

    token_info = sp_oauth.refresh_access_token(token_info["refresh_token"])
    session["token_info"] = token_info
    return token_info

@app.route("/test") # is it working?
def test():
    return "Test route is working!"

# debug
print("Environment Variables Loaded:")
print(f"CLIENT_ID: {CLIENT_ID}")
print(f"CLIENT_SECRET: {'****' if CLIENT_SECRET else 'Not Set'}")
print(f"SPOTIPY_REDIRECT_URI: {SPOTIFY_REDIRECT_URI}")
print(f"SCOPE: {SCOPE}")



if __name__ == "__main__":
    # debug mode only for local development
    is_local = os.getenv("RENDER") is None  # check if running locally
    app.run(debug=is_local, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
