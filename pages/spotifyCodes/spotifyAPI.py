import spotipy
from spotipy.oauth2 import SpotifyOAuth
import webbrowser
import requests
import requests
import time
import streamlit as st

from dotenv import load_dotenv
import os

# from PIL import Image
# import base64
# from io import BytesIO
# import json

load_dotenv("resources/spotipy_credentials.env")
# SPOTIPY_CLIENT_ID = os.getenv("SPOTIPY_CLIENT_ID")
# SPOTIPY_CLIENT_SECRET = os.getenv("SPOTIPY_CLIENT_SECRET")
# SPOTIPY_REDIRECT_URI = os.getenv("SPOTIPY_REDIRECT_URI")

SPOTIPY_CLIENT_ID = st.secrets("SPOTIPY_CLIENT_ID")
SPOTIPY_CLIENT_SECRET = st.secrets("SPOTIPY_CLIENT_SECRET")
SPOTIPY_REDIRECT_URI = st.secrets("SPOTIPY_REDIRECT_URI")
SCOPE = 'user-read-private user-read-email user-library-read user-library-modify playlist-modify-private playlist-modify-public ugc-image-upload'.replace(' ','+')  # the scope of access you require
RESPONSE_TYPE = 'code'
TOKEN_ENDPOINT = 'https://accounts.spotify.com/api/token'

# Authenticating for client side
sp_oauth = SpotifyOAuth(
        client_id=SPOTIPY_CLIENT_ID,
        client_secret=SPOTIPY_CLIENT_SECRET,
        redirect_uri=SPOTIPY_REDIRECT_URI,
        scope="user-follow-read user-read-recently-played user-library-read user-top-read user-read-currently-playing user-library-modify playlist-modify-private playlist-modify-public"
    )

sp = spotipy.Spotify(auth_manager=sp_oauth)

def get_user_id(access_token):
    # Set the endpoint URL
    url = 'https://api.spotify.com/v1/me'
    
    # Set the authorization header
    headers = {'Authorization': f'Bearer {access_token}'}
    
    # Send a GET request to the endpoint
    response = requests.get(url, headers=headers)
    
    # Extract the user ID from the response
    if response.status_code == 200:
        user_id = response.json()['id']
        return user_id
    else:
        return None
    
def get_saved_tracks(access_token,limit):
    # Set the endpoint URL
    url = f'https://api.spotify.com/v1/me/tracks?limit={limit}'
    
    # Set the authorization header
    headers = {'Authorization': f'Bearer {access_token}'}
    
    # Send a GET request to the endpoint
    response = requests.get(url, headers=headers)
    
    # Extract the saved tracks from the response
    if response.status_code == 200:
        saved_tracks = response.json()['items']
        return saved_tracks
        
    else:
        return None
    
# def set_playlist_cover(playlist_id, access_token):
#     with open("resources/images/senpai.jpg", "rb") as image_file:
#         image_base64 = base64.b64encode(image_file.read()).decode('utf-8')

#         url = f'https://api.spotify.com/v1/playlists/{playlist_id}'
#         data = {'images': [{'data': image_base64}]}
#         headers = {'Authorization': f'Bearer {access_token}', 'Content-Type': 'application/json'}
#         headers['Content-Length'] = str(len(json.dumps(data)))
#         response = requests.put(url, headers=headers, data=json.dumps(data))

#         if response.status_code == 202:
#             print('Playlist profile image set successfully!')
#         else:
#             print(response.status_code)
#             print('Error setting playlist profile image.')