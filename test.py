import sqlite3

def recreate_playlist_history_table():
    """
    Recreate the playlist_history table with the correct schema.
    """
    conn = sqlite3.connect("app.db")
    cursor = conn.cursor()

    # Drop the table if it exists
    cursor.execute("DROP TABLE IF EXISTS playlist_history")

    # Create the table with the correct schema
    cursor.execute("""
        CREATE TABLE playlist_history (
            user_id TEXT,
            playlist_name TEXT,
            playlist_id TEXT,
            song_uris TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()
    print("Recreated the playlist_history table with the correct schema.")

if __name__ == "__main__":
    recreate_playlist_history_table()
