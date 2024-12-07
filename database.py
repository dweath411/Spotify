import sqlite3


def initialize_db():
    """initialize the sqlite database for storing selected songs."""
    conn = sqlite3.connect("app.db")
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS selected_songs (
            user_id TEXT,
            song_uri TEXT
        )
        """
    )
    conn.commit()
    conn.close()


def add_selected_songs(user_id, songs):
    """add songs to the database."""
    conn = sqlite3.connect("app.db")
    cursor = conn.cursor()
    cursor.executemany("INSERT INTO selected_songs (user_id, song_uri) VALUES (?, ?)", [(user_id, s) for s in songs])
    conn.commit()
    conn.close()


def get_selected_songs(user_id):
    """retrieve selected songs for a user."""
    conn = sqlite3.connect("app.db")
    cursor = conn.cursor()
    cursor.execute("SELECT song_uri FROM selected_songs WHERE user_id = ?", (user_id,))
    songs = [row[0] for row in cursor.fetchall()]
    conn.close()
    return songs
