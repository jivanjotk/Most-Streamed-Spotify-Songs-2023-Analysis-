
import requests
import pandas as pd
import time

# Function to get Spotify access token
def get_spotify_token(client_id, client_secret):
    auth_url = 'https://accounts.spotify.com/api/token'
    auth_response = requests.post(auth_url, {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret,
    })
    auth_data = auth_response.json()
    return auth_data['access_token']


def search_track(track_name, artist_name, token, max_retries=3):
    query = f"{track_name} artist:{artist_name}"
    url = f"https://api.spotify.com/v1/search?q={query}&type=track"
    retries = 0
    while retries < max_retries:
        try:
            response = requests.get(url, headers={'Authorization': f'Bearer {token}'})
            response.raise_for_status()  # Raise an exception for 4xx and 5xx status codes
            json_data = response.json()
            first_result = json_data['tracks']['items'][0]
            track_id = first_result['id']
            return track_id
        except (KeyError, IndexError, requests.exceptions.HTTPError) as e:
            # Handle exceptions and retry
            retries += 1
            print(f"Error occurred: {e}. Retrying... (Attempt {retries}/{max_retries})")
            time.sleep(1)  # Wait for 1 second before retrying
    print(f"Max retries reached. Unable to fetch track details for '{track_name} - {artist_name}'.")
    return None


# Function to search for a track and get its ID
def search_track(track_name, artist_name, token):
    query = f"{track_name} artist:{artist_name}"
    url = f"https://api.spotify.com/v1/search?q={query}&type=track"
    response = requests.get(url, headers={
        'Authorization': f'Bearer {token}'
    })
    json_data = response.json()
    try:
        first_result = json_data['tracks']['items'][0]
        track_id = first_result['id']
        return track_id
    except (KeyError, IndexError):
        return None

# Function to get track details
def get_track_details(track_id, token):
    url = f"https://api.spotify.com/v1/tracks/{track_id}"
    response = requests.get(url, headers={
        'Authorization': f'Bearer {token}'
    })
    json_data = response.json()
    image_url = json_data['album']['images'][0]['url']
    return image_url

# Your Spotify API Credentials
client_id = '1f59ab5da293466489f550372cdb2ec9'
client_secret = 'a64d73c10d92410ebd1280317d35d9a4'

# Get Access Token
access_token = get_spotify_token(client_id, client_secret)

# Read your DataFrame (replace 'your_file.csv' with the path to your CSV file)
df_spotify = pd.read_csv('spotify-2023.csv', encoding='ISO-8859-1')

# Loop through each row to get track details and add to DataFrame
for i, row in df_spotify.iterrows():
    track_id = search_track(row['track_name'], row['artist_name'], access_token)
    if track_id:
        image_url = get_track_details(track_id, access_token)
        df_spotify.at[i, 'image_url'] = image_url

# Save the updated DataFrame (replace 'updated_file.csv' with your desired output file name)
df_spotify.to_csv('updated_file.csv', index=False)
