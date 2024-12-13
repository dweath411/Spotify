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
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.commit()
    conn.close()


def save_playlist_history(user_id, playlist_name, playlist_id):
    """
    save details of a created playlist.

    args:
        user_id (str): spotify user id.
        playlist_name (str): name of the playlist.
        playlist_id (str): id of the playlist.
    """
    conn = sqlite3.connect("app.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO playlist_history (user_id, playlist_name, playlist_id) VALUES (?, ?, ?)",
        (user_id, playlist_name, playlist_id),
    )
    conn.commit()
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
