import spotipy
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from spotipy import SpotifyClientCredentials
import os

# Scripts
from data_extraction import target_playlist_extraction, save_data

# Credentials are stored using Streamlit secrets keeper.
def retrieve_target_playlist(playlist_url, playlist_name):
    client_credentials_manager = SpotifyClientCredentials(client_id=st.secrets['CLIENT_ID'],
                                                          client_secret=st.secrets['CLIENT_SECRET'])
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    df_target = target_playlist_extraction(sp, playlist_url, playlist_name)  # Generate target playlist dataframe
    save_data(df_target)

    root_path = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    file_path = os.path.join(root_path, 'data', 'tracks.csv')
    df = pd.read_csv(file_path, index_col=0)  # Read in stored tracks dataframe
    print("New shape", df.shape)
    return df


st.title("MIAS")
st.markdown(
    "MIAS is the **M**usically **I**lliterate **A**id **S**ystem designed to help developing artists expand their "
    "performance playlist")

playlist_url = st.text_input("Please insert playlist url here")
playlist_name = st.text_input("Please insert the playlist name here")

if playlist_url != "" and playlist_name != "" and 'target_retrieved' not in st.session_state:
    st.session_state['target_retrieved'] = True
    df = retrieve_target_playlist(playlist_url, playlist_name)

