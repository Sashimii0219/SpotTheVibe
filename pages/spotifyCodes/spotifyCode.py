import pandas as pd
import spotipy.util as util
import re
from datetime import datetime
from dateutil.relativedelta import relativedelta
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import numpy as np
import streamlit as st

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MinMaxScaler

from pages.spotifyCodes.spotifyAPI import *

# Retrieve saved tracks of a user through API call, then process the data to fit our recommender system
def retrieve_saved_tracks(access_token):
    #Retrieve 50 most recently saved songs
    results_saved = get_saved_tracks(access_token,50)

    # Need to account for no saved_tracks
    ##########

    saved_song = []
    for idx, item in enumerate(results_saved):
        added_time = results_saved[idx]['added_at'].replace("T", " ").replace("Z", "")
        month_added = relativedelta(datetime.now(), datetime.strptime(added_time, '%Y-%m-%d %H:%M:%S')).months
        year = int(results_saved[idx]['track']['album']['release_date'][:4])
        name = results_saved[idx]['track']['name'] 
    
        artist = results_saved[idx]['track']['artists'][0]['name'] 
        artist_info = sp.artist(results_saved[idx]['track']["artists"][0]["external_urls"]["spotify"])
        popularity = artist_info['popularity']
        genres = artist_info["genres"]
    

        album = results_saved[idx]['track']['album']['name'] 
        track_id = results_saved[idx]['track']['id']
        saved_song.append([track_id, name, artist, album, month_added, added_time, genres, year, popularity])
    
    saved_df = pd.DataFrame(data=saved_song, columns=['id', 'name', 'artist', 'album', 'month_added','date_added', 'genres', 'year', 'popularity'])
    saved_df.set_index('id')
    
    song_charact = pd.DataFrame()
    for id in saved_df['id']:
        info = pd.DataFrame(sp.audio_features(id), index=[id])
        song_charact = pd.concat([info, song_charact])

    user_df = pd.merge(saved_df, song_charact,  how='inner')
    return user_df

# Application of OHE
# Simple function to create OHE features
def ohe_prep(df, column, new_name): 
    """ 
    Create One Hot Encoded features of a specific column

    Parameters: 
        df (pandas dataframe): Spotify Dataframe
        column (str): Column to be processed
        new_name (str): new column name to be used
        
    Returns: 
        tf_df: One hot encoded features 
    """
    
    tf_df = pd.get_dummies(df[column])
    feature_names = tf_df.columns
    tf_df.columns = [new_name + "|" + str(i) for i in feature_names]
    tf_df.reset_index(drop = True, inplace = True)    
    return tf_df

# Function to build entire feature set
def create_feature_set(df, float_cols):
    """ 
    Process spotify df to create a final set of features that will be used to generate recommendations

    Parameters: 
        df (pandas dataframe): Spotify Dataframe
        float_cols (list(str)): List of float columns that will be scaled 
        
    Returns: 
        final: final set of features 
    """
    
    # Tfidf genre lists
    tfidf = TfidfVectorizer(stop_words=None)
    tfidf_matrix =  tfidf.fit_transform(df['genre_filtered2'])
    genre_df = pd.DataFrame(tfidf_matrix.toarray())
    genre_df.columns = ['genre' + "|" + i for i in tfidf.get_feature_names_out()]
    genre_df.reset_index(drop = True, inplace=True)
    genre_df

    # Explicity_ohe = ohe_prep(df, 'explicit','exp')    
    year_ohe = ohe_prep(df, 'year_bins','year_bins') * 0.2
    popularity_ohe = ohe_prep(df, 'popularity_red','pop') * 0.35

    # Scale float columns
    floats = df[float_cols].reset_index(drop = True)
    scaler = MinMaxScaler()
    floats_scaled = pd.DataFrame(scaler.fit_transform(floats), columns = floats.columns) * 0.2

    # Concanenate all features
    final = pd.concat([genre_df, floats_scaled, popularity_ohe, year_ohe], axis = 1)
     
    # Add song id
    final['id']=df['id'].values
    
    return final

# Function to generate features
def generate_playlist_feature(complete_feature_set, weight_factor, valence_weight_factor, access_token):
    """ 
    Summarize a user's playlist into a single vector

    Parameters: 
        complete_feature_set (pandas dataframe): Dataframe which includes all of the features for the spotify songs
        playlist_df (pandas dataframe): playlist dataframe
        weight_factor (float): float value that represents the recency bias. The larger the recency bias, the most priority recent songs get. Value should be close to 1. 
        
    Returns: 
        playlist_feature_set_weighted_final (pandas series): single feature that summarizes the playlist
        complete_feature_set_nonplaylist (pandas dataframe): 
    """
    playlist_df = retrieve_saved_tracks(access_token)

    complete_feature_set_playlist = complete_feature_set[complete_feature_set['id'].isin(playlist_df['id'].values)]#.drop('id', axis = 1).mean(axis =0)
    complete_feature_set_playlist = complete_feature_set_playlist.merge(playlist_df[['id','date_added', 'month_added']], on = 'id', how = 'inner')
    complete_feature_set_nonplaylist = complete_feature_set[~complete_feature_set['id'].isin(playlist_df['id'].values)]#.drop('id', axis = 1)
    complete_feature_set_playlist
    
    playlist_feature_set = complete_feature_set_playlist.sort_values('date_added',ascending=False)
    most_recent_date = playlist_feature_set.iloc[0,-1]
    
#     for ix, row in playlist_feature_set.iterrows():
#         playlist_feature_set.loc[ix,'months_from_recent'] = int((most_recent_date.to_pydatetime() - row.iloc[-1].to_pydatetime()).days / 30)
        
    playlist_feature_set['weight'] = playlist_feature_set['month_added'].apply(lambda x: weight_factor ** (-x))
    
    playlist_feature_set_weighted = playlist_feature_set.copy()
#     print(playlist_feature_set_weighted.iloc[:,:-4].columns)
    playlist_feature_set_weighted.update(playlist_feature_set_weighted.iloc[:,:-4].mul(playlist_feature_set_weighted.weight,0))
    playlist_feature_set_weighted['valence'] = playlist_feature_set_weighted['valence'].apply(lambda x: x ** valence_weight_factor)
    playlist_feature_set_weighted['energy'] = playlist_feature_set_weighted['energy'].apply(lambda x: x ** valence_weight_factor)
    playlist_feature_set_weighted['danceability'] = playlist_feature_set_weighted['danceability'].apply(lambda x: x ** valence_weight_factor)
    playlist_feature_set_weighted_final = playlist_feature_set_weighted.iloc[:, :-4]
    #playlist_feature_set_weighted_final['id'] = playlist_feature_set['id']
    
    return playlist_feature_set_weighted_final.sum(axis = 0), complete_feature_set_nonplaylist

# Generate recommendations
def generate_playlist_recos(df, features, nonplaylist_features):
    """ 
    Pull songs from a specific playlist.

    Parameters: 
        df (pandas dataframe): spotify dataframe
        features (pandas series): summarized playlist feature
        nonplaylist_features (pandas dataframe): feature set of songs that are not in the selected playlist
        
    Returns: 
        non_playlist_df_top: Top x recommendations for that playlist
    """
    
    non_playlist_df = df[df['id'].isin(nonplaylist_features['id'].values)]
    non_playlist_df['sim'] = cosine_similarity(nonplaylist_features.drop('id', axis = 1).values, features.values.reshape(1, -1))[:,0]
    non_playlist_df_top = non_playlist_df.sort_values('sim',ascending = False).head(50)
    non_playlist_df_top['url'] = non_playlist_df_top['id'].apply(lambda x: sp.track(x)['album']['images'][1]['url'])
    
    return non_playlist_df_top

# Add playlist to Spotify
def add_to_spotify(playlist_name, recommendation):
    userid = sp.current_user()['id']
    results_playlist = sp.user_playlist_create(userid, name=playlist_name, public=False, collaborative=False, description='This is a playlist generated by a Spotify Recommender System.')
    playlist_id = results_playlist['id']

    songs = list(recommendation['id'])
    sp.playlist_add_items(playlist_id, songs, position=None)

    # set_playlist_cover(playlist_id,st.session_state.access_token)

@st.cache_data
def load_spotify_df():
    return pd.read_csv("spotify_df_latest.csv")

spotify_df = load_spotify_df()
bins = int(np.ceil((spotify_df['year'].max() - spotify_df['year'].min())/10))
spotify_df['year_bins'] = pd.cut(spotify_df['year'], bins = bins)
float_cols = spotify_df.dtypes[spotify_df.dtypes == 'float64'].index.values
# complete_feature_set = create_feature_set(spotify_df, float_cols=float_cols)#.mean(axis = 0)
# valence_weight_factor = 0.5
# complete_feature_set_playlist_vector, complete_feature_set_nonplaylist = generate_playlist_feature(complete_feature_set,  1.2, valence_weight_factor)

