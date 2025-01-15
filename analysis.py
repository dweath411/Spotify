import matplotlib.pyplot as plt  
from io import BytesIO  # handles in-memory byte streams for image data
import base64  # encodes binary data as base64 strings
import spotipy  # spotify python library for API access
from textwrap import fill  

# define default play counts for different time ranges
DEFAULT_PLAY_COUNTS = {
    "short_term": 50,  # default estimated play count for the last 4 weeks
    "medium_term": 300,  # default estimated play count for the last 6 months
    "long_term": 500,  # default estimated play count for the last year
}

def fetch_top_tracks(sp, time_range="short_term", limit=10):
    """
    fetch the top tracks for a user based on the selected time range.

    args:
        sp (spotipy.Spotify): spotify client.
        time_range (str): time range ('short_term', 'medium_term', 'long_term').
        limit (int): number of tracks to fetch.

    returns:
        list: list of top tracks with their cumulative playtime.
    """
    play_count = DEFAULT_PLAY_COUNTS.get(time_range, 50)  # get default play count for the time range
    results = sp.current_user_top_tracks(time_range=time_range, limit=limit)  # fetch top tracks from spotify
    # process tracks to calculate cumulative playtime
    tracks = [
        {
            "name": item["name"],  # track name
            "artist": ", ".join([artist["name"] for artist in item["artists"]]),  # artist(s) name(s)
            "duration_ms": item["duration_ms"] * play_count,  # estimate total playtime based on default play count
        }
        for item in results["items"]
    ]
    return tracks  # return the processed list of tracks

def generate_analysis_plot(tracks, time_range):
    """
    generate a bar plot for the top tracks.

    args:
        tracks (list): list of tracks with playtime.
        time_range (str): time range for the analysis.

    returns:
        str: base64-encoded string of the plot image.
    """
    import textwrap  # ensures text wrapping for better readability in plots

    # prepare data for plotting
    song_names = [f"{t['name']} ({t['artist']})" for t in tracks]  # format track names with artist info
    wrapped_song_names = [textwrap.fill(name, width=25) for name in song_names]  # wrap long track names for readability
    durations = [t["duration_ms"] / (1000 * 60 * 60) for t in tracks]  # convert milliseconds to hours for playtime

    # create the bar plot
    plt.figure(figsize=(12, 8))  # set figure size to enhance plot visibility
    plt.barh(wrapped_song_names, durations, color="#1DB954")  # create a horizontal bar plot with spotify green color
    plt.xlabel("Listening Hours", fontsize=12, labelpad=10)  # x-axis label with additional spacing
    plt.ylabel("Track Name", fontsize=12, labelpad=10)  # y-axis label with additional spacing
    plt.title(f"Your Most Played Songs ({time_range.replace('_', ' ').title()})", fontsize=16, pad=15)  # plot title
    plt.gca().invert_yaxis()  # invert y-axis for better readability
    plt.subplots_adjust(left=0.3, right=0.95, top=0.9, bottom=0.1)  # adjust plot margins
    plt.tight_layout()  # optimize layout for a cleaner appearance

    # save the plot as a base64-encoded string
    buffer = BytesIO()  # create an in-memory buffer for the plot image
    plt.savefig(buffer, format="png", bbox_inches="tight")  # save the plot to the buffer in PNG format
    buffer.seek(0)  # reset buffer position to the beginning
    plot_data = base64.b64encode(buffer.getvalue()).decode("utf-8")  # encode buffer content to base64
    buffer.close()  # close the buffer to free memory

    return plot_data  # return the base64-encoded string of the plot
