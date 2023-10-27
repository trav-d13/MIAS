import spotipy
import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from spotipy import SpotifyClientCredentials
import os

# Scripts
from data_processing import target_playlist_extraction, save_data, update_tracking
from similarity import CosineSimilarity


## METHODS  ##
def retrieve_target_playlist(url: str, name: str):
    """ This method gathers all the playlist song features and merges this data into the tracks dataset.

        Note: credentials are stored using Streamlit secrets keeper

    Args:
        url (str): The url for the spotify playlist
        name (str): The name of the spotify playlist
    Returns:
        playlist (DataFrame): The playlist features as a DataFrame
    """
    client_credentials_manager = SpotifyClientCredentials(client_id=st.secrets['CLIENT_ID'],
                                                          client_secret=st.secrets[
                                                              'CLIENT_SECRET'])  # Set up Spotify Credentials
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    playlist = target_playlist_extraction(sp, url, name)  # Generate target playlist dataframe
    save_data(playlist)  # Save the playlist tracks into the larger tracks dataset
    playlist_df = playlist_to_df(playlist)
    return playlist_df


def access_tracks():
    """Method enables access to saved track information.

    Returns:
        df (DataFrame): The dataframe containing all feature information of saved tracks
    """
    root_path = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    file_path = os.path.join(root_path, 'data', 'tracks.csv')
    df = pd.read_csv(file_path, index_col=0)  # Read in stored tracks dataframe
    return df


def playlist_to_df(playlist: dict):
    target_df = pd.DataFrame.from_dict(playlist)
    return target_df


## UI ##
if 'playlist_links' not in st.session_state:  # Initialize playlist history states
    st.session_state.playlist_links = []
    st.session_state.playlist_names = []
    st.session_state.similarity = None
    print("States initialized")

st.title("MIAS")
st.markdown(
    "MIAS is the **M**usically **I**lliterate **A**id **S**ystem designed to help developing artists expand their "
    "performance playlist")

st.header("Search ")
playlist_url = st.text_input("Please insert playlist url here")
playlist_name = st.text_input("Please insert the playlist name here")
submit_button = st.button("Submit")

if submit_button:
    if playlist_url != "" and playlist_name != "":
        df_playlist = retrieve_target_playlist(playlist_url, playlist_name)
        df_tracks = access_tracks()

        st.session_state.similarity = CosineSimilarity(df_playlist, df_tracks)
        st.session_state.similarity.calculate_similarity()
        update_tracking(df_tracks)

        st.session_state.playlist_links.append(playlist_url)
        st.session_state.playlist_names.append(playlist_name)

with st.expander("Search History", expanded=False):
    if len(st.session_state.playlist_links) == 0:
        st.markdown('No search history yet...')
    else:
        for name, url in zip(st.session_state.playlist_names, st.session_state.playlist_links):
            st.write(name + " | " + url)

st.header('Search Results')
if st.session_state.similarity is None:
    st.write('Please perform a search first')
else:
    # Recommended Results
    st.markdown("#### Recommended Tracks")

    col1, col2 = st.columns(2)
    count = 0
    rec_df = st.session_state.similarity.get_top_n(30)
    for index, row in rec_df.iterrows():
        song_name = row['names']
        spotify_uri = row['uris']
        embed_code = f'<iframe src="https://open.spotify.com/embed/track/{spotify_uri.split(":")[-1]}" ' \
                     'width="300" height="80" frameborder="0" allowtransparency="true" allow="encrypted-media"></iframe>'

        if count % 2 == 0:
            with col1:
                st.markdown(embed_code, unsafe_allow_html=True)
        else:
            with col2:
                st.markdown(embed_code, unsafe_allow_html=True)
        count += 1

    # Similarity visualization
    data_df = pd.DataFrame(st.session_state.similarity.access_similarity_scores(),
                           columns=['sim_score'])

    st.markdown("#### Playlist Similarity to Track Dataset")
    sns.set_style('whitegrid')
    fig, axes = plt.subplots(1, 1, figsize=(12, 4))

    g = sns.histplot(data=data_df,
                     x='sim_score',
                     kde=True,
                     color='red',
                     ax=axes)

    axes.set_yscale('log')
    axes.set_xscale('log')
    axes.set_xlabel('Similarity Values (Log)')
    axes.set_ylabel('Frequency')

    st.pyplot(plt)
