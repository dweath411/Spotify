from flask import Flask, request, redirect, render_template, url_for, session
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
from spotipy_app.playlist import create_or_update_playlist, get_user_playlists
from database import initialize_db, add_selected_songs, get_selected_songs
import os

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

    sp = Spotify(auth=token_info["access_token"])  # reinitialize Spotify client
    playlist_id = request.form["playlist_id"]  # get selected playlist ID from form
    overwrite = request.form.get("overwrite") == "on"  # check if overwrite is selected

    # get user's Spotify ID and previously selected songs
    user_id = sp.me()["id"]
    selected_songs = get_selected_songs(user_id)

    # create or update the playlist
    create_or_update_playlist(sp, user_id, playlist_id, selected_songs, overwrite)

    return "Playlist updated successfully!"


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 5001)))
