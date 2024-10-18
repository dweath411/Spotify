'''
The following is needed if I determine that I don't want to create a new playlist per release radar.
This solution prevents the playlist from accumulating songs week after week. 
It will always contain the latest 20 songs selected from your large playlist.

# the existing Release Radar playlist ID (this is the one that gets updated every week)
# release_radar_playlist_id = 'Throwback Radar 2.0'  # replace with your permanent Release Radar playlist ID

# clear the Release Radar playlist before adding new songs
# clear_playlist(release_radar_playlist_id)

# add the newly selected songs to the Release Radar playlist
# add_songs_to_playlist(release_radar_playlist_id, new_songs)

# add songs to a sub-playlist
# sub_playlist_id = 'Songs' # replace with your sub-playlist ID
# clear_playlist(sub_playlist_id) # clear sub-playlist if there are contents in it already
# add_songs_to_playlist(sub_playlist_id, new_songs) # add new songs to sub-playlist


---------------
This following chunk of code is to create new playlists weekly, instead of updating just one.
It also creates a playlist full of songs previously added to origin radar, so you have a history.

# create new playlist for the week
# current_week = datetime.now().strftime("%Y-%m-%d")
# new_playlist_id = create_new_playlist(f"Origin Radar - {current_week}")
print("Playlist created with new songs!")
# add the newly selected songs to new playlist and historic playlist
# add_songs_to_playlist(new_playlist_id, new_songs)

#historic_playlist_id = create_new_playlist(f"Origin Radar History")
# add_songs_to_playlist(historic_playlist_id, new_songs)

---------
Old create new playlist function
# function to create a new playlist for the current user
def create_new_playlist(name, description = "Throwback Radar 2.0"):
    user_id = sp.current_user()['id'] # get the current authenticated user ID
    playlist = sp.user_playlist_create(user_id, name, description = description) # create new playlist with a name and description
    return playlist['id'] # return ID of the newly created playlist

'''


'''
chatgpt add on
import logging

# Configure logging to capture warnings and errors in a log file
logging.basicConfig(filename='playlist_errors.log', level=logging.WARNING, 
                    format='%(asctime)s:%(levelname)s:%(message)s')

# Step 1: Check if the large playlist contains any tracks
if len(large_playlist_tracks) == 0:
    print("Error: The large playlist is empty. Add some songs to it first.")
    logging.error("The large playlist is empty. Cannot select 20 unique songs.")
    exit(1)  # Exit the script since there's no point in continuing without tracks

# Step 2: Get the list of track URIs from the large playlist, excluding previously selected tracks
track_uris = [track['track']['uri'] for track in large_playlist_tracks if track['track']['uri'] not in selected_songs]

# Check if there are no unique tracks available after excluding the selected ones
if len(track_uris) == 0:
    print("Error: No more unique tracks available to select from the large playlist.")
    logging.error("No unique tracks are available. Cannot select 20 new songs.")
    exit(1)  # Exit the script since no unique songs are available

# Step 3: Handle cases where fewer than 20 unique tracks are available
if len(track_uris) < 20:
    print(f"Warning: Only {len(track_uris)} unique songs are available. "
          "All available songs will be added to the playlist.")
    logging.warning(f"Only {len(track_uris)} unique songs available. Adding all available songs.")
    new_songs = track_uris  # Add all available unique songs
else:
    new_songs = random.sample(track_uris, 20)  # Select 20 random unique songs

# Save selected songs to avoid duplication in future selections
selected_songs.extend(new_songs)

# Save the updated selected songs list to avoid duplicates next week
with open('selected_songs.json', 'w') as f:
    json.dump(selected_songs, f)


'''