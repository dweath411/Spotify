import sqlite3  # sqlite3 module for database operations

def initialize_db():
    """
    initialize the SQLite database for storing selected songs.
    """
    conn = sqlite3.connect("app.db")  # connect to (or create) the database file
    cursor = conn.cursor()  # create a cursor object to execute SQL commands

    # create a table for storing user-selected songs if it doesn't already exist
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS selected_songs (
            user_id TEXT,  -- column for storing the user's ID
            song_uri TEXT  -- column for storing the song's unique URI
        )
        """
    )
    conn.commit()  # commit the changes to the database
    conn.close()  # close the connection to the database

def get_selected_songs(user_id):
    """
    retrieve selected songs for a specific user.

    Args:
        user_id (str): the ID of the user.

    Returns:
        list: a list of song URIs selected by the user.
    """
    conn = sqlite3.connect("app.db")  # connect to the database
    cursor = conn.cursor()  # create a cursor object

    # execute a query to fetch song URIs associated with the given user ID
    cursor.execute("SELECT song_uri FROM selected_songs WHERE user_id = ?", (user_id,))
    songs = [row[0] for row in cursor.fetchall()]  # extract URIs from the query results
    conn.close()  # close the connection to the database
    return songs  # return the list of song URIs

def add_selected_songs(user_id, songs):
    """
    add selected songs to the database for a specific user.

    Args:
        user_id (str): the ID of the user.
        songs (list): a list of song URIs to add.
    """
    conn = sqlite3.connect("app.db")  # connect to the database
    cursor = conn.cursor()  # create a cursor object

    # use executemany to insert multiple rows into the selected_songs table
    cursor.executemany(
        "INSERT INTO selected_songs (user_id, song_uri) VALUES (?, ?)",
        [(user_id, s) for s in songs]  # prepare a tuple for each song
    )
    conn.commit()  # commit the changes to the database
    conn.close()  # close the connection to the database
