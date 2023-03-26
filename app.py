import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import time
from datetime import datetime
from io import StringIO
import pickle
import requests
import webbrowser

from PIL import Image

def get_image(img_name):
    return Image.open(f'resources/images/{img_name}')

from pages.spotifyCodes import spotifyAPI

st.set_page_config(
    page_title="SpotTheVibe",
    page_icon="👋",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.sidebar.success("Select a page above.")
st.write("# Music Recommender System")
st.write("## Hohoho looking for some song recommendations?  👋")
st.write("This is a Spotify Song Recommender System created by our team for Business Intelligence and Analytics Club's Data Associate Program.")

st.header("The Team:")
col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.image(get_image("zhengfeng.jpg"), caption='Zhengfeng')

with col2:
    st.image(get_image("yuanzhi.png"), caption='Yuanzhi')

with col3:
    st.image(get_image("kowsalya.png"), caption='Kowsalya')

with col4:
    st.image(get_image("jackson.jpg"), caption='Jackson')

with col5:
    st.image(get_image("senpai.jpg"), caption='Boss')
# st.table(pd.DataFrame({"Name":['Zhengfeng','Yuanzhi','Kowsalya','Jackson']}))
auth_url = f'https://accounts.spotify.com/authorize?client_id={spotifyAPI.SPOTIPY_CLIENT_ID}&response_type={spotifyAPI.RESPONSE_TYPE}&redirect_uri={spotifyAPI.SPOTIPY_REDIRECT_URI}&scope={spotifyAPI.SCOPE}'

st.header("To get your song recommendations, follow the steps below:")
st.markdown(f'1. Press on <b><a href="{auth_url}" target="_blank">this</a></b> to log in and authenticate.', unsafe_allow_html=True)
st.write("2. Go to 'Input' tab to pull your saved tracks.")
st.write("3. Adjust the number of songs to generate, and their popularity.")
st.write("4. Press on 'Please Generate Recommendations For Me Sir!' for your song recommendations.")
st.write("5. Evaluate your recommendations under the 'Recommender' tab.")

# if st.button('Authorize'):
    # # Generate the authorization URL and redirect the user to it
    # auth_url = f'https://accounts.spotify.com/authorize?client_id={spotifyAPI.SPOTIPY_CLIENT_ID}&response_type={spotifyAPI.RESPONSE_TYPE}&redirect_uri={spotifyAPI.SPOTIPY_REDIRECT_URI}&scope={spotifyAPI.SCOPE}'
    # webbrowser.open(auth_url)
    # # st.write('Please follow the link below to authenticate with Spotify:')
    # # st.markdown(f'<a href="{auth_url}">{auth_url}</a>', unsafe_allow_html=True)
    # # Once the user has authenticated and been redi rected back to the app,
    # # extract the authorization code from the redirect URI and display it

if 'code' in st.experimental_get_query_params():
    auth_code = st.experimental_get_query_params()['code'][0]
    # st.write(f'Authorization code: {auth_code}')

    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    data = {'grant_type': 'authorization_code', 'code': auth_code, 'redirect_uri': spotifyAPI.SPOTIPY_REDIRECT_URI, 'client_id': spotifyAPI.SPOTIPY_CLIENT_ID, 'client_secret': spotifyAPI.SPOTIPY_CLIENT_SECRET}
    response = requests.post(spotifyAPI.TOKEN_ENDPOINT, headers=headers, data=data)
        
    # Extract the access token from the response
    if response.status_code == 200:
        access_token = response.json()['access_token']
        expires_in = response.json()['expires_in']
        refresh_token = response.json()['refresh_token']
        expiration_time = time.time() + expires_in
        # st.write(f'Access token: {access_token}')
        # st.write(f'Expires in: {expires_in}')
        # st.write(f'Refresh token: {refresh_token}')

        st.session_state.access_token = access_token
        st.session_state.expiration_time = expiration_time
        st.session_state.refresh_token = refresh_token
        st.success("Successfully Verified!🔥")
    else:
         st.write(f'Error: {response.status_code}')

else:
    st.warning("Waiting for verifications...")

# Initialize session states
if 'show_recommendation' not in st.session_state:
    st.session_state.show_recommendation = False

# Things to explore:
# Include page to explain what we learn and the things we use for this webapp
# Create .env file (DONE)
# Add more emojis and clean up code, more commments too
# Deploy Web App
