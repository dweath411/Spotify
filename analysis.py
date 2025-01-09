import matplotlib.pyplot as plt
from io import BytesIO
import base64
import spotipy
from datetime import datetime

def fetch_top_tracks(sp, time_range="short_term", limit=10):
    """
    Fetch the top tracks for a user based on the selected time range.

    Args:
        sp (spotipy.Spotify): Spotify client.
        time_range (str): Time range ('short_term', 'medium_term', 'long_term').
        limit (int): Number of tracks to fetch.

    Returns:
        list: List of top tracks with their playtime.
    """
    results = sp.current_user_top_tracks(time_range=time_range, limit=limit)
    tracks = [
        {
            "name": item["name"],
            "artist": ", ".join([artist["name"] for artist in item["artists"]]),
            "duration_ms": item["duration_ms"],
        }
        for item in results["items"]
    ]
    return tracks

def generate_analysis_plot(tracks, time_range):
    """
    Generate a bar plot for the top tracks.

    Args:
        tracks (list): List of tracks with playtime.

    Returns:
        str: Base64-encoded string of the plot image.
    """
    song_names = [f"{t['name']} ({t['artist']})" for t in tracks]
    durations = [t["duration_ms"] / (1000 * 60 * 60) for t in tracks]  # Convert ms to hours

    plt.figure(figsize=(10, 6))
    plt.barh(song_names, durations, color="#1DB954")
    plt.xlabel("Hours Played")
    plt.ylabel("Top Songs")
    plt.title(f"Top Songs ({time_range.replace('_', ' ').title()})")
    plt.gca().invert_yaxis()

    buffer = BytesIO()
    plt.savefig(buffer, format="png", bbox_inches="tight")
    buffer.seek(0)
    plot_data = base64.b64encode(buffer.getvalue()).decode("utf-8")
    buffer.close()

    return plot_data
