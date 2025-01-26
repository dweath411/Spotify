# Spotify Origin Radar
**Spotify Origin Radar** is a web application that allows users to create personalized weekly playlists based on their existing Spotify library. The current features are: playlist curation, analysis of listening habits, and playlist data export, and removing duplicate tracks from playlists. Spotify Origin Radar aims to enhance your Spotify experience.

## Features
**Spotify Authentication:** Log in securely via Spotify OAuth 2.0. Your data is secure through Spotify.

**Custom Playlist Creation:** Generate a curated "Origin Radar" playlist weekly, pulling from your selected source playlist. Generate a playlist of recommendations as well.

**No Duplicates:** Prevent duplicate songs in curated playlists with built-in validation.

**Top Tracks Analysis:** Visualize your most played tracks for the past week, past 6 months, or past year.
  * Generate interactive bar charts showing the cumulative playtime of your top songs.
  * Estimate listening time using custom logic and default play counts for each time range.

**Playlist Export:** Export playlist data (e.g., song details, durations, popularity) to a CSV file.

**Duplicate Removal:** Detect and remove duplicate tracks from any playlist.

**Responsive UI:** User-friendly interface styled to align with Spotify's theme.

## Spotipy Documentation
For more information about the Spotify API wrapper used in this application, visit the [Spotipy Documentation](https://spotipy.readthedocs.io/en/2.24.0/).

### Table of Contents
Prerequisites
Setup Instructions
Environment Variables
Project Structure
Features in Detail
Deployment on Render
Contributing
License

## Prerequisites
Before setting up Spotify Origin Radar, ensure you have the following:

* A **Spotify Developer Account** with an application registered in the Spotify Developer Dashboard.
* Python version 3.7 or higher.
* Access to a web browser for authentication during the Spotify login process.

## Setup Instructions
1. **Clone the Repository:**

`git clone https://github.com/yourusername/spotify-origin-radar.git
cd spotify-origin-radar`

2. **Install Dependencies:** Use the provided `requirements.txt` to install all dependencies:

`pip install -r requirements.txt`

3. **Set Up Environment Variables:** Spotify API credentials and app configurations must be set up. For local deployment, create a `.env` file in the project root:

```bash
CLIENT_ID=your_spotify_client_id
CLIENT_SECRET=your_spotify_client_secret
SPOTIPY_REDIRECT_URI=http://localhost:5000/callback # or your Render deployment callback link
FLASK_APP=app.py
SCOPE="user-top-read user-read-email playlist-modify-public playlist-modify-private playlist-read-private user-library-read"
```

**Explanation of required scopes**

`user-top-read`: Allows the app to access the user's top artists and tracks.

`user-read-email`: Grants access to the user's email address.

`playlist-modify-public`: Allows modifying the user's public playlists.

`playlist-modify-private`: Allows modifying the user's private playlists.

`playlist-read-private`: Grants access to read the user's private playlists.

`user-library-read`: Allows reading the user's saved tracks (required for /v1/me/tracks endpoint).

`user-read-recently-played`: Required to retrieve the user’s recently played tracks using the `/v1/me/player/recently-played` endpoint.

4. **Run the Application:** Launch the app locally:

`python app.py`

The app will be accessible at `http://localhost:5000` (or whatever `redirect_uri` you set).

5. **Access the Deployed App (Optional):** If deploying to Render, update your Spotify Developer Dashboard's redirect URI to match your Render URL (e.g., `https://yourappname.onrender.com/callback`).


---

## Environment Variables

| Variable Name         | Description                                             |
|-----------------------|---------------------------------------------------------|
| `CLIENT_ID`           | Spotify application client ID.                          |
| `CLIENT_SECRET`       | Spotify application client secret.                      |
| `SPOTIPY_REDIRECT_URI`| Redirect URI for Spotify OAuth.                         |
| `FLASK_APP`           | Entry point for Flask application (default: `app.py`).  |
| `SCOPE`               | Permissions required for Spotify API (see code).        |

## Project Structure

```bash
spotify-origin-radar/
│
├── app.py             # main application file
├── playlist.py        # functions for playlist handling
├── analysis.py        # functions for top tracks analysis
├── database.py        # SQLite database functions
├── templates/         # HTML templates (e.g., index.html, dashboard.html)
├── static/            # CSS, images, and other static assets
├── requirements.txt   # project dependencies
├── .env.example       # example environment variable file
└── README.md          # project documentation
```
## Features in Detail

### 1. Spotify Authentication
Users authenticate via Spotify OAuth 2.0. The application ensures secure login and token handling, including automatic token refreshes when expired.

### 2. Custom Playlist Creation
* Users can select any playlist as a source.
* A curated "Origin Radar" playlist is created with 20 random songs, avoiding duplicates from previous weeks.
  * This curated playlist takes songs from which you already have in your playlist, it does generate recommendations.
* Users can also select a playlist that has a minimum of 50 songs in it, using that playlist as the source you can generate recommendations. 

### 3. Top tracks analyis
Analyze your most played tracks over three time ranges:

**Past Month:** Short-term listening trends.

**Past 6 Months:** Medium-term trends.

**Past Year:** Long-term trends.

The analysis includes:

* A bar chart visualization of cumulative playtime for the top 10 songs.
* Playtime estimation based on track duration and predefined play counts. *Spotify doesn't give exact track listening data, so an estimation is establish.*

### 4. Playlist Export
Export playlist details to a CSV file, including:

* Playlist ID and user-input name.
* Track details (name, artist, album).
* Track duration in seconds.
* Popularity scores and release dates.

### 5. Duplicate Removal
* Scans for duplicate songs in a playlist.
* Removes all duplicates in one click from the selected playlist.

## Deployment on Render
1. **Deploy the App:** Push your code to a repository (e.g., GitHub) and link it to a new Render web service.

2. **Set Environment Variables:** Add your Spotify API credentials and configuration under the "Environment" section of Render.

3. **Set Redirect URI:** Update the Spotify Developer Dashboard with your Render URL (e.g., `https://yourappname.onrender.com/callback`).

4. **Launch:** Access your deployed app at your Render-provided URL

### Contributing
Contributions are welcome! Please fork the repository, make your changes, and submit a pull request. Ensure all changes are documented and tested. If you plan on making any changes without pull request, please credit this repository. 

## License
This project is licensed under the MIT License
