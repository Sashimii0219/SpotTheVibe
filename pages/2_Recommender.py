import streamlit as st
import pandas as pd

from pages.spotifyCodes import spotifyCode

st.title("Recommendations")

if st.session_state.show_recommendation:
    recommendations = pd.read_csv("recommended_songs.csv")
    print(recommendations)
    if len(recommendations.index) != 0:
        recommendation = recommendations[['name','artists','year','genre_filtered2']]
        st.dataframe(recommendation)

        like_songs = st.radio(
        "Do you like them songs?",
        ('Yes', 'Maybe', 'No'), index=2, key='radio_option')

        if like_songs == "Yes" or like_songs == "Maybe":
            st.subheader("Consider adding them playlist to your spotify? ʕ •ᴥ•ʔ")
            playlist_name = st.text_input('Playlist Title', 'DAP')
            st.write('The current playlist name is', playlist_name)
            if st.button('Add them in baby', help='Yes'):
                spotifyCode.add_to_spotify(playlist_name,recommendations)
                st.balloons()
                st.snow()
                st.success("Playlist Added! Enjoy :)")

        else:
            st.subheader("ಠ_ಠ ಠ_ಠ ಠ_ಠ ಠ_ಠ ಠ_ಠ ಠ_ಠ")
            st.snow()
    else:
        st.error("NO RECOMMENDATIONS ಠ_ಠ")
else:
    st.write("Go to 'Input' tab to generate recommendations!!!")
    st.error("NO RECOMMENDATIONS ಠ_ಠ")

# To Explore
# https://docs.streamlit.io/library/advanced-features/theming