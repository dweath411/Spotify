from flask import Flask, request, redirect, render_template, url_for, session
from apscheduler.schedulers.background import BackgroundScheduler
import os
from main import create_or_update_playlist

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.urandom(24)  # Needed for session management

# Initialize scheduler for weekly playlist updates
scheduler = BackgroundScheduler(daemon=True)
scheduler.start()

# Home route with form to collect playlist ID
@app.route('/')
def home():
    return render_template('index.html')  # Render form for user input

# Form submission route to set up playlist details
@app.route('/submit', methods=['POST'])
def submit():
    # Get playlist ID and Spotify user ID from form
    large_playlist_id = request.form['large_playlist_id']
    user_id = request.form['user_id']
    
    # Store user data in session
    session['large_playlist_id'] = large_playlist_id
    session['user_id'] = user_id
    
    # Initial playlist creation
    create_or_update_playlist(user_id, large_playlist_id)
    
    # Schedule weekly job for updating the playlist
    scheduler.add_job(func=create_or_update_playlist, trigger="interval", weeks=1, args=[user_id, large_playlist_id])

    return redirect(url_for('success'))  # Redirect to success page

# Success page route
@app.route('/success')
def success():
    return "Your Origin Radar playlist has been created and will update weekly!"

# Clear session data and unschedule jobs if needed
@app.route('/logout')
def logout():
    session.clear()  # Clear session data
    scheduler.remove_all_jobs()  # Remove all scheduled jobs
    return "Logged out and scheduled updates removed."

if __name__ == '__main__':
    app.run(debug=True)


'''
home(): Renders the main web page (HTML) form to collect Spotify credentials (client_id and client_secret)
submit(): Handles the form submission and redirects to execute the Spotify logic after credentials are entered.
'''