from flask import Flask, request, render_template, redirect, url_for
from main import run_spotify_logic # import spotify logic function

app = Flask(__name__) # initialize Flask app

# route the home page
@app.route('/')
def home():
    return render_template('index.html') # render HTML template to get credentials

# route for handling Spotify authentication form submission
@app.route('/spotify_auth', methods = ['POST']) 
def spotify_auth():
    client_id = request.form['client_id'] # client_id from form input
    client_secret = request.form['client_secret'] # client_secret from form input
    redirect_uri = "http://localhost:5000/callback" # set a redirect URI

    try: 
        # redirect to run script with provided credentials
        return redirect(url_for('run_spotify_scipt', client_id = client_id, client_secret = client_secret))
    except Exception as e:
        return f"Error during authentication: {e}" # return error message
    
# route to execute Spotify script once credentials are entered
@app.route('/run_spotify_script')
def run_spotify_script():
    client_id = request.args.get('client_id') # get the client_id from URL parameters
    client_secret = request.args.get('client_secret') # get the client_secret from URL parameters

    try:
        # run spotify logic and display the result message (failure or success)
        message = run_spotify_logic(client_id, client_secret)
        return message
    except Exception as e:
        return f"Error while running Spotfiy script: {e}" # return error if it doesn't run
    
if __name__ == '__main__':
    app.run(debug=True) # run the Flask app in debug mode 


'''
home(): Renders the main web page (HTML) form to collect Spotify credentials (client_id and client_secret)
spotify_auth(): Handles the form submission and redirects to execute the Spotify logic after credentials are entered.
run_spotify_script(): Executes the logic to update the playlist, using the passed credentials.
'''