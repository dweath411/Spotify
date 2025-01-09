import matplotlib.pyplot as plt
from io import BytesIO
import base64
import spotipy
from textwrap import fill

# Define default play counts for different time ranges
DEFAULT_PLAY_COUNTS = {
    "short_term": 50,  # last 4 weeks
    "medium_term": 300,  # last 6 months
    "long_term": 500,  # last year
}

def fetch_top_tracks(sp, time_range="short_term", limit=10):
    """
    Fetch the top tracks for a user based on the selected time range.

    Args:
        sp (spotipy.Spotify): Spotify client.
        time_range (str): Time range ('short_term', 'medium_term', 'long_term').
        limit (int): Number of tracks to fetch.

    Returns:
        list: List of top tracks with their cumulative playtime.
    """
    play_count = DEFAULT_PLAY_COUNTS.get(time_range, 50)  # Default play count
    results = sp.current_user_top_tracks(time_range=time_range, limit=limit)
    tracks = [
        {
            "name": item["name"],
            "artist": ", ".join([artist["name"] for artist in item["artists"]]),
            "duration_ms": item["duration_ms"] * play_count,  # Estimate total playtime
        }
        for item in results["items"]
    ]
    return tracks

def generate_analysis_plot(tracks, time_range):
    """
    Generate a bar plot for the top tracks.

    Args:
        tracks (list): List of tracks with playtime.
        time_range (str): Time range for the analysis.

    Returns:
        str: Base64-encoded string of the plot image.
    """
    import textwrap

    # Prepare data
    song_names = [f"{t['name']} ({t['artist']})" for t in tracks]
    wrapped_song_names = [textwrap.fill(name, width=25) for name in song_names]  # Wrap long names
    durations = [t["duration_ms"] / (1000 * 60 * 60) for t in tracks]  # Convert ms to hours

    # Create plot
    plt.figure(figsize=(12, 8))  # Larger figure size
    plt.barh(wrapped_song_names, durations, color="#1DB954")
    plt.xlabel("Listening Hours", fontsize=12, labelpad=10)
    plt.ylabel("Track Name", fontsize=12, labelpad=10)
    plt.title(f"Your Most Played Songs ({time_range.replace('_', ' ').title()})", fontsize=16, pad=15)
    plt.gca().invert_yaxis()
    plt.subplots_adjust(left=0.3, right=0.95, top=0.9, bottom=0.1)  # Adjust margins
    plt.tight_layout()  # Automatic layout adjustment

    # Save and encode plot
    buffer = BytesIO()
    plt.savefig(buffer, format="png", bbox_inches="tight")
    buffer.seek(0)
    plot_data = base64.b64encode(buffer.getvalue()).decode("utf-8")
    buffer.close()

    return plot_data

# def generate_analysis_plot(tracks, time_range):
#     """
#     Generate a bar plot for the top tracks.

#     Args:
#         tracks (list): List of tracks with playtime.

#     Returns:
#         str: Base64-encoded string of the plot image.
#     """
#     # Wrap long track names for better display
#     song_names = [fill(f"{t['name']} ({t['artist']})", width=25) for t in tracks]
#     durations = [t["duration_ms"] / (1000 * 60 * 60) for t in tracks]  # Convert ms to hours

#     plt.figure(figsize=(10, 6))
#     plt.barh(song_names, durations, color="#1DB954")
#     plt.xlabel("Hours Played")
#     plt.ylabel("Top Songs")
#     plt.title(f"Top Songs ({time_range.replace('_', ' ').title()})")
#     plt.gca().invert_yaxis()

#     buffer = BytesIO()
#     plt.savefig(buffer, format="png", bbox_inches="tight")
#     buffer.seek(0)
#     plot_data = base64.b64encode(buffer.getvalue()).decode("utf-8")
#     buffer.close()

    return plot_data

