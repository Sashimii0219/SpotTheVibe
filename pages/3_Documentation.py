import streamlit as st

st.title("Documentation")
st.subheader("This page documents our learning process, breaking down and explaining the logic behind our spotify music recommender system:")
with st.expander("Creating our Model"):
    link = "https://www.kaggle.com/datasets/yamaerenay/spotify-dataset-19212020-600k-tracks"
    st.write("### Dataset:")
    st.write(f"""The dataset that we used for this model comes from <a href="{link}">Kaggle</a>, 
    containing audio features, popularity metrics, and other details of 600k+ songs extracted from Spotify.""", unsafe_allow_html=True)
    # st.image("Kaggle")
    st.write("### Data Cleaning and Pre-processing:")
    st.write("""Due to dataset size and computing power limitations, below are the steps we did to pre-process our data for training:
    - Merge our song dataset with the artist dataset to extract the song genres.
    - Extracted the release year of the song.
    - Binned the year into decades and popularity into 5-point buckets.
    - Kept the top 20 song genres of each decade and categorised the rest under others.
     """)
    st.write("""
    ### Feature Engineering:
    - One hot encoded years bin, popularity
    - Create TF-IDF features off of genres to prioritise less frequent keyword terms (genres)
     """)
    st.code("""
    # One-hot encode columns
    def ohe_prep(df, column, new_name): 
    tf_df = pd.get_dummies(df[column])
    feature_names = tf_df.columns
    tf_df.columns = [new_name + "|" + str(i) for i in feature_names]
    tf_df.reset_index(drop = True, inplace = True)
    return tf_df
    """)
    st.code("""
    # Generating feature set
    def create_feature_set(df, float_cols):
    tfidf = TfidfVectorizer()
    tfidf_matrix =  tfidf.fit_transform(df['consolidates_genre_lists'].apply(lambda x: " ".join(x)))
    genre_df = pd.DataFrame(tfidf_matrix.toarray())
    genre_df.columns = ['genre' + "|" + i for i in tfidf.get_feature_names()]
    genre_df.reset_index(drop = True, inplace=True)

    #explicity_ohe = ohe_prep(df, 'explicit','exp')    
    year_ohe = ohe_prep(df, 'year','year') * 0.5
    popularity_ohe = ohe_prep(df, 'popularity_red','pop') * 0.15
    """)

with st.expander("Utilising Spotipy (Spotify API)"):
    st.markdown("""
    The next step was to utilise the Spotify API to retrieve user's saved tracks. In order to do that,
    we first need to authenticate the user and retrieve their access token:
    """)
    st.code("""
    # Send user to login page for Spotify to allow access
    auth_url = f'https://accounts.spotify.com/authorize?client_id={spotifyAPI.SPOTIPY_CLIENT_ID}&
    response_type={spotifyAPI.RESPONSE_TYPE}&redirect_uri={spotifyAPI.SPOTIPY_REDIRECT_URI}&scope={spotifyAPI.SCOPE}'

    # Streamlit function to extract the authorization code
    if 'code' in st.experimental_get_query_params():
    auth_code = st.experimental_get_query_params()['code'][0]

    # Use the authorization code to send a POST request to get the access token
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    data = {'grant_type': 'authorization_code', 'code': auth_code, 'redirect_uri': spotifyAPI.SPOTIPY_REDIRECT_URI, 'client_id': spotifyAPI.SPOTIPY_CLIENT_ID, 'client_secret': spotifyAPI.SPOTIPY_CLIENT_SECRET}
    response = requests.post(spotifyAPI.TOKEN_ENDPOINT, headers=headers, data=data)
        
    # Extract the access token from the response
    if response.status_code == 200:
        access_token = response.json()['access_token']
        expires_in = response.json()['expires_in']
        refresh_token = response.json()['refresh_token']
        expiration_time = time.time() + expires_in

        # Utilise st.session_state to save the access token, refresh token, and expiration timer
        st.session_state.access_token = access_token
        st.session_state.expiration_time = expiration_time
        st.session_state.refresh_token = refresh_token
    """)

    st.markdown("""
    Once we have the access token, we are able to retrieve information that we need for the recommender to function,
    like the user's saved track (example below):
    """)
    st.code("""
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
    """)
    st.write("""
    Last step before our recommendation would be to generate a final playlist vector (by averaging all the values) 
    based on the user's saved tracks, with a weight multiplied to values of each song based on the recency of it 
    (when it was saved), prioritizing more recent additions.
    """)

with st.expander("Using the Recommender"):
    st.write(""" ### Cosine Similarity:
    With the dataset (excluded the songs in our saved tracks) and final playlist vector ready, the next step was to determine the cosine similarity of all the
    songs in the dataset and sort them according by most to least similar to the final playlist vectors:
    """)
    st.code("""
    def generate_playlist_recos(df, features, nonplaylist_features, num_to_gen):
    
    non_playlist_df = df[df['id'].isin(nonplaylist_features['id'].values)]
    non_playlist_df['sim'] = cosine_similarity(nonplaylist_features.drop('id', axis = 1).values, features.values.reshape(1, -1))[:,0]
    non_playlist_df_top = non_playlist_df.sort_values('sim',ascending = False).head(num_to_gen)
    non_playlist_df_top['url'] = non_playlist_df_top['id'].apply(lambda x: sp.track(x)['album']['images'][1]['url'])
    
    return non_playlist_df_top
    """)

with st.expander("Developing our Streamlit Webpage / Final Wrap Up"):
    st.write(""" ### Rationale for using Streamlit
    We decided to use Streamlit to deploy our model as it was the easiest to use and the most intuitive, suitable for this particular project.

    ### Notable Streamlit features used:
    - st.session.state: to share variables like access_token between each page for each user session.
    - st.experimental_get_query_params: returns query parameter in browser's URL bar, particularly the authorization code that got returned.
    - st.button: to enable all sorts of features like extracting saved tracks, or generating recommendations.
    """)
