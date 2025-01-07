import sqlite3

def initialize_db():
    """Initialize the SQLite database for storing selected songs and playlist history."""
    conn = sqlite3.connect("app.db")
    cursor = conn.cursor()
    # table for selected songs
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS selected_songs (
            user_id TEXT,
            song_uri TEXT
        )
        """
    )
    # table for playlist history
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

def add_song_uris_column():
    """
    Add the 'song_uris' column to the 'playlist_history' table if it doesn't already exist.
    """
    conn = sqlite3.connect("app.db")
    cursor = conn.cursor()

    # Check if 'song_uris' column exists
    cursor.execute("PRAGMA table_info(playlist_history)")
    columns = [column[1] for column in cursor.fetchall()]
    if "song_uris" not in columns:
        cursor.execute("ALTER TABLE playlist_history ADD COLUMN song_uris TEXT")
        conn.commit()
        print("Added 'song_uris' column to 'playlist_history' table.")
    else:
        print("'song_uris' column already exists in 'playlist_history' table.")
    
    conn.close()

if __name__ == "__main__":
    add_song_uris_column()


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

def add_to_playlist_history(user_id, playlist_name, playlist_id, song_uris):
    """Add playlist history to the database."""
    conn = sqlite3.connect("app.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO playlist_history (user_id, playlist_name, playlist_id, song_uris) VALUES (?, ?, ?, ?)",
        (user_id, playlist_name, playlist_id, ','.join(song_uris))
    )
    conn.commit()
    conn.close()

def get_playlist_history(user_id):
    """Retrieve playlist history for a user."""
    conn = sqlite3.connect("app.db")
    cursor = conn.cursor()
    cursor.execute("SELECT playlist_name, playlist_id, song_uris, timestamp FROM playlist_history WHERE user_id = ?", (user_id,))
    playlists = cursor.fetchall()
    conn.close()
    return playlists
