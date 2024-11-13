from flask import Flask, request, render_template, redirect, url_for
from main import run_spotify_logic  # import the main logic function

app = Flask(__name__)  # initialize Flask application

# route for home page displaying the input form
@app.route('/')
def home():
    return render_template('index.html')  # render the HTML form page

# route to handle the form submission
@app.route('/submit', methods=['POST'])
def submit():
    # retrieve the large playlist ID from user input
    large_playlist_id = request.form['large_playlist_id']

    try:
        # run the main Spotify logic
        run_spotify_logic(large_playlist_id)
        return redirect(url_for('success'))  # redirect to success page
    except Exception as e:
        return f"Error: {e}"  # display error if something goes wrong

# success page route
@app.route('/success')
def success():
    return "Playlist updated successfully!"  # success message for the user

if __name__ == '__main__':
    app.run(debug=True)  # start the Flask application in debug mode


'''
home(): Renders the main web page (HTML) form to collect Spotify credentials (client_id and client_secret)
submit(): Handles the form submission and redirects to execute the Spotify logic after credentials are entered.
'''