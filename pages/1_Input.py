import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import pandas as pd
import spotipy.util as util
from datetime import datetime
from dateutil.relativedelta import relativedelta
import requests
import time
from pathlib import Path

from pages.spotifyCodes import spotifyCode, spotifyAPI

spotify_df = spotifyCode.spotify_df

if 'access_token' in st.session_state:
    access_token = st.session_state.access_token
    # st.write(access_token)

# Check if access token has expired before making any API requests
if 'access_token' in st.session_state and 'expiration_time' in st.session_state:
    if time.time() >= st.session_state.expiration_time:
        # If the access token expired, refresh it using the refresh token
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        data = {'grant_type': 'refresh_token', 'refresh_token': st.session_state.refresh_token, 'client_id': spotifyAPI.SPOTIPY_CLIENT_ID, 'client_secret': spotifyAPI.SPOTIPY_CLIENT_SECRET}
        response = requests.post(spotifyAPI.TOKEN_ENDPOINT, headers=headers, data=data)

        # Extract new access token and expiration time
        if response.status_code == 200:
            access_token = response.json()['access_token']
            expires_in = response.json()['expires_in']
            expiration_time = time.time() + expires_in
            st.session_state.access_token = access_token
            st.session_state.expiration_time = expiration_time

if 'but_a' not in st.session_state:
    st.session_state.disabled = True

if 'saved_tracks' not in st.session_state:
    st.session_state.saved_tracks = False

def change_reco():
    st.session_state.show_recommendation = not st.session_state.show_recommendation

st.title("Input")
st.write("Press on button to pull saved tracks from your spotify account!")

if st.button('Pull Saved Tracks', help='Oh yeah pull it!'):

    if 'access_token' not in st.session_state:
        st.error("Authenticate first!")
    
    else:
        saved_tracks = spotifyCode.retrieve_saved_tracks(access_token)

        if len(saved_tracks) != 0:
            st.write('Here\'s your saved tracks!')
            st.dataframe(saved_tracks)
            st.balloons()
            st.snow()
            st.session_state.saved_tracks = True

        else:
            st.error("No saved tracks bro 💀")
            st.session_state.saved_tracks = False

# Number of Songs to Recommend
st.markdown("## Number of Songs to Recommend")
no_of_songs = st.slider('How many songs to recommend?', 0, 50, 25)
if no_of_songs > 0:
    st.write("Recommend me ", no_of_songs, ' songs please sir...')
    if st.session_state.saved_tracks:
        st.session_state.disabled = False
else:
    st.info("I'm just here for the vibes 🕺")
    st.session_state.disabled = True
    st.balloons()
    st.snow()

# Pouplarity range of songs
st.markdown("## Popularity Range")
popularity = st.slider('How popular do you want your songs???', 0, 100, (50,100))
# st.write(popularity)

if popularity[0] >= 50 and popularity[1] == 100:
    st.write("Give me the pop songs! 🕺")

elif popularity[0] >= 50:
    st.write("Give me the good songs! 🕺")

elif popularity[0] <= 50 and popularity[1] > 50:
    st.write("Give me all the songs! 🕺")

elif popularity[1] <= 50:
    st.write("Hell yeah i like shitty ass songs! 🕺")

# Session state things
# def change_reco():
#     st.session_state.show_recommendation = not st.session_state.show_recommendation

# Button to generate recommendations
if st.button('Please Generate Recommendations For Me Sir!', help='Yes', key='but_a', disabled=st.session_state.disabled):

    with st.spinner("Generating Recommendations..."):
        try:
        # Generating Recommendations
            spotify_df = spotify_df[(spotify_df['popularity'] > popularity[0]) & (spotify_df['popularity'] < popularity[1])]

            complete_feature_set = spotifyCode.create_feature_set(spotify_df, float_cols=spotifyCode.float_cols)
            valence_weight_factor = 0.5
            complete_feature_set_playlist_vector, complete_feature_set_nonplaylist = spotifyCode.generate_playlist_feature(complete_feature_set,  1.2, valence_weight_factor, access_token)
            recommendation = spotifyCode.generate_playlist_recos(spotify_df, complete_feature_set_playlist_vector, complete_feature_set_nonplaylist).head(no_of_songs)
            # st.dataframe(recommendation)
            
            st.session_state.df = recommendation
            # print(file_path)
            st.balloons()
            st.snow()
            st.success("Recommendations generated, please proceed to recommender page! :heart:")
            st.session_state.show_recommendation = True
        except:
            st.warning("Recommendations failed to generate, please readjust your parameters ⚠️")
            st.session_state.show_recommendation = False
