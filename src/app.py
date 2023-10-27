import spotipy
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from spotipy import SpotifyClientCredentials
import os

# Scripts
from data_extraction import target_playlist_extraction, save_data


## METHODS  ##
def retrieve_target_playlist(url: str, name: str):
    """ This method gathers all of the playlist song features and merges this data into the tracks dataset.

        Note: credentials are stored using Streamlit secrets keeper

    Args:
        url (str): The url for the spotify playlist
        name (str): The name of the spotify playlist
    Returns:
        playlist (dict): The playlist features as a dictionary
    """
    client_credentials_manager = SpotifyClientCredentials(client_id=st.secrets['CLIENT_ID'],
                                                          client_secret=st.secrets['CLIENT_SECRET'])  # Set up Spotify Credentials
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    playlist = target_playlist_extraction(sp, url, name)  # Generate target playlist dataframe
    save_data(playlist)  # Save the playlist tracks into the larger tracks dataset
    return playlist


def access_tracks():
    """Method enables access to saved track information.

    Returns:
        df (DataFrame): The dataframe containing all feature information of saved tracks
    """
    root_path = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    file_path = os.path.join(root_path, 'data', 'tracks.csv')
    df = pd.read_csv(file_path, index_col=0)  # Read in stored tracks dataframe
    return df


## UI ##
if 'playlist_links' not in st.session_state:  # Initialize playlist history states
    st.session_state.playlist_links = []
    st.session_state.playlist_names = []
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
        df_target = retrieve_target_playlist(playlist_url, playlist_name)

        st.session_state.playlist_links.append(playlist_url)
        st.session_state.playlist_names.append(playlist_name)
        print(st.session_state.playlist_names)
        print(st.session_state.playlist_links)

with st.expander("Search History", expanded=False):
    if len(st.session_state.playlist_links) == 0:
        st.markdown('No search history yet...')
    else:
        for name, url in zip(st.session_state.playlist_names, st.session_state.playlist_links):
            st.write(name + " | " + url)


