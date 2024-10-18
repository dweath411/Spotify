from flask import Flask, request, render_template, redirect, url_for
from main import run_spotify_logic # import spotify logic function

app = Flask(__name__) # initialize Flask app

# route the home page
@app.route('/')
def home():
    return render_template('index.html') # render HTML template to get credentials

# route for handling Spotify authentication form submission
@app.route('/submit', methods = ['POST']) 
def submit():
    client_id = request.form['client_id'] # client_id from form input
    client_secret = request.form['client_secret'] # client_secret from form input
    large_playlist_id = request.form['large_playlist_id'] # get users playlist of choice
    # pass ID to spotify script
    try: 
        run_spotify_logic(client_id, client_secret, large_playlist_id)
        # redirect to run script with provided credentials
        return redirect(url_for('success'))
    except Exception as e:
        return f"Error during authentication: {e}" # return error message

@app.route('/success') # route to show sucess after playlist is updated
def success():
    return "Playlist updated successfully"     
   
if __name__ == '__main__':
    app.run(debug=False, port=5001) # run the Flask app in debug mode 


'''
home(): Renders the main web page (HTML) form to collect Spotify credentials (client_id and client_secret)
submit(): Handles the form submission and redirects to execute the Spotify logic after credentials are entered.
'''