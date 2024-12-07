# Spotify Origin Radar

Spotify Origin Radar is a web application that allows users to create a weekly curated playlist from their existing Spotify playlists. Users can log in with their Spotify account, select a source playlist, and have a custom "Origin Radar" playlist updated weekly.

## Features
- Authenticate with Spotify via OAuth.
- Select a source playlist from a dropdown menu.
- Automatically create or update a weekly curated playlist.
- Ensure no repeated songs are added using an SQLite database.

## Prerequisites
- A Spotify Developer account with registered application credentials.
- Python 3.7 or higher.

## Setup Instructions

1. **Clone the Repository**:
   ```bash
   git clone #insert github link
   cd spotify-origin-radar

2. **Install the dependencies**:
    pip install -r requirements.txt

3. **Setup the environment variables**
    CLIENT_ID=your_spotify_client_id
    CLIENT_SECRET=your_spotify_client_secret
    
    This is only required if you are not running the app off of the Render deployment.
4. **Run the application**
    python app.py

5. **Access the app**
    Open http://localhost:5000 in your browser.
    This may vary user to user.

Ensure your Spotify app's redirect URI matches the deployed URL (e.g., https://yourappname.onrender.com/callback)
