import sqlite3

def update_playlist_history_schema():
    """
    Update the playlist_history table schema to include the created_at column.
    """
    conn = sqlite3.connect("app.db")
    cursor = conn.cursor()

    # Rename the old table
    cursor.execute("ALTER TABLE playlist_history RENAME TO playlist_history_old")

    # Create the new table with the correct schema
    cursor.execute("""
        CREATE TABLE playlist_history (
            user_id TEXT,
            playlist_name TEXT,
            playlist_id TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Copy data from the old table
    cursor.execute("""
        INSERT INTO playlist_history (user_id, playlist_name, playlist_id)
        SELECT user_id, playlist_name, playlist_id FROM playlist_history_old
    """)

    # Drop the old table
    cursor.execute("DROP TABLE playlist_history_old")

    conn.commit()
    conn.close()

    print("Database schema updated successfully!")

if __name__ == "__main__":
    update_playlist_history_schema()
