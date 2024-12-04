from flask import Flask, request, redirect, render_template, url_for, session
from apscheduler.schedulers.background import BackgroundScheduler
import os
import json
from main import create_or_update_playlist

# initialize flask app
app = Flask(__name__)
app.secret_key = os.urandom(24)  # needed for session management

# initialize scheduler for weekly playlist updates
scheduler = BackgroundScheduler(daemon=True)
scheduler.start()

# json file to store user session data persistently
SESSION_FILE = "user_session.json"


# helper function to load session data from json
def load_session_data():
    if os.path.exists(SESSION_FILE):
        try:
            with open(SESSION_FILE, 'r') as file:
                return json.load(file)
        except Exception as e:
            print(f"Error loading session data: {e}")
            return {}
    return {}


# helper function to save session data to json
def save_session_data(data):
    try:
        with open(SESSION_FILE, 'w') as file:
            json.dump(data, file)
    except Exception as e:
        print(f"Error saving session data: {e}")


# home route with form to collect playlist id
@app.route('/')
def home():
    return render_template('index.html')  # render form for user input


# form submission route to set up playlist details
@app.route('/submit', methods=['POST'])
def submit():
    try:
        # get playlist id and spotify user id from form
        large_playlist_id = request.form['large_playlist_id']
        user_id = request.form['user_id']

        # store user data in session (and persistently in json)
        session['large_playlist_id'] = large_playlist_id
        session['user_id'] = user_id

        # persist session data to json
        session_data = {"large_playlist_id": large_playlist_id, "user_id": user_id}
        save_session_data(session_data)

        # initial playlist creation
        create_or_update_playlist(user_id, large_playlist_id)

        # schedule weekly job for updating the playlist
        scheduler.add_job(
            func=create_or_update_playlist,
            trigger="interval",
            weeks=1,
            args=[user_id, large_playlist_id],
            id=f"update_playlist_{user_id}"  # unique job id
        )

    except Exception as e:
        return f"Error: {str(e)}"

    return redirect(url_for('success'))  # redirect to success page


# success page route
@app.route('/success')
def success():
    return "Your Origin Radar playlist has been created and will update weekly!"


# load session and reschedule jobs on app startup
@app.before_first_request
def load_jobs():
    session_data = load_session_data()
    if session_data:
        large_playlist_id = session_data.get("large_playlist_id")
        user_id = session_data.get("user_id")
        if large_playlist_id and user_id:
            # reschedule the job if data exists
            scheduler.add_job(
                func=create_or_update_playlist,
                trigger="interval",
                weeks=1,
                args=[user_id, large_playlist_id],
                id=f"update_playlist_{user_id}"  # unique job id
            )


# clear session data and unschedule jobs if needed
@app.route('/logout')
def logout():
    session.clear()  # clear session data
    if os.path.exists(SESSION_FILE):
        os.remove(SESSION_FILE)  # delete persistent session file
    scheduler.remove_all_jobs()  # remove all scheduled jobs
    return "Logged out and scheduled updates removed."


if __name__ == "__main__":
    app.run(debug=False, host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))


'''
home(): Renders the main web page (HTML) form to collect Spotify credentials (client_id and client_secret)
submit(): Handles the form submission and redirects to execute the Spotify logic after credentials are entered.
'''