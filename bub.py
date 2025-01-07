import sqlite3

def check_table_schema():
    """
    Print the schema of the playlist_history table.
    """
    conn = sqlite3.connect("app.db")
    cursor = conn.cursor()

    # Query the schema
    cursor.execute("PRAGMA table_info(playlist_history)")
    schema = cursor.fetchall()
    print("Current playlist_history schema:")
    for column in schema:
        print(column)

    conn.close()

if __name__ == "__main__":
    check_table_schema()
