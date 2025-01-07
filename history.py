import sqlite3


def initialize_history_db():
    """
    initialize the sqlite database for storing playlist history.
    """
    conn = sqlite3.connect("app.db")
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS playlist_history (
            user_id TEXT,
            playlist_name TEXT,
            playlist_id TEXT,
            song_uris TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.commit()
    conn.close()

# def save_playlist_history(user_id, playlist_name, playlist_id, song_uris):
#     """
#     Save details of a created playlist.

#     Args:
#         user_id (str): Spotify user ID.
#         playlist_name (str): Name of the playlist.
#         playlist_id (str): ID of the playlist.
#         song_uris (list): URIs of the songs in the playlist.
#     """
#     conn = sqlite3.connect("app.db")
#     cursor = conn.cursor()
#     cursor.execute(
#         "INSERT INTO playlist_history (user_id, playlist_name, playlist_id, song_uris) VALUES (?, ?, ?, ?)",
#         (user_id, playlist_name, playlist_id, ','.join(song_uris)),
#     )
#     conn.commit()
#     conn.close()

def save_playlist_history(user_id, playlist_name, playlist_id, song_uris):
    """
    Save details of a created playlist.

    Args:
        user_id (str): Spotify user ID.
        playlist_name (str): Name of the playlist.
        playlist_id (str): ID of the playlist.
        song_uris (list): URIs of the songs in the playlist.
    """
    # Debugging: Output the data being saved
    print(f"Saving playlist: {playlist_name}, ID: {playlist_id}, Songs: {song_uris}")

    conn = sqlite3.connect("app.db")
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO playlist_history (user_id, playlist_name, playlist_id, song_uris) VALUES (?, ?, ?, ?)",
            (user_id, playlist_name, playlist_id, ','.join(song_uris)),
        )
        conn.commit()
        print(f"Playlist {playlist_name} saved successfully!")
    except sqlite3.Error as e:
        print(f"Error saving playlist history: {e}")
    finally:
        conn.close()


def get_user_history(user_id):
    """
    retrieve the playlist history for a user.

    args:
        user_id (str): spotify user id.

    returns:
        list: a list of past playlists with names and ids.
    """
    conn = sqlite3.connect("app.db")
    cursor = conn.cursor()
    cursor.execute(
        "SELECT playlist_name, playlist_id, created_at FROM playlist_history WHERE user_id = ? ORDER BY created_at DESC",
        (user_id,),
    )
    history = cursor.fetchall()
    conn.close()
    return history
