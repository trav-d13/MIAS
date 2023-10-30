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


def feature_def_section():
    """This method creates the features section in the Streamlit app.

    Specifically, it creates the feature definitions drop down information.
    """
    st.markdown(
        '**For advanced recommender personalization please select the features to be weighted (have more importance) to '
        'your search**')

    with st.expander('Feature Definitions'):
        feature_defs = retrieve_feature_defs()
        for definition in feature_defs.split('\\n'):
            st.markdown(definition)


def search_history_section():
    """This method creates the search history section of the Streamlit application.

    This section provides a drop-down that displays the search history in the from
    playlist name | playlist url
    """
    with st.expander("Search History", expanded=False):
        if len(st.session_state.playlist_links) == 0:
            st.markdown('No search history yet...')
        else:
            for name, url in zip(st.session_state.playlist_names, st.session_state.playlist_links):
                st.write(name + " | " + url)


def search_results_section():
    """This methods creates the search results section in the Streamlit app.

    This can be broken down into two sub-sections.
    1. Spotify Recommendations
    2. The similarity visualization

    Note, if no playlist or name is given, this section is replaced by a `Please perform search first` message
    """
    st.header('Search Results')
    if st.session_state.similarity is None:
        st.write('Please perform a search first')
    else:
        # Recommended Results
        display_spotify_recommendations()

        # Similarity visualization
        fig_1 = similarity_visualization()
        st.pyplot(fig_1)


def playlist_submission():
    """Method handles the process that follows the clicking of the `submit` button

    The process is as follows:
    - The given playlist tracks are retrieved.
    - The tracks dataset is read in
    - Similarity is calculated
    - Streamlit session states are updated
    """
    df_playlist = retrieve_target_playlist(playlist_url, playlist_name)
    df_tracks = access_tracks()

    st.session_state.similarity = CosineSimilarity(df_playlist, df_tracks, st.session_state.weighted_features)
    st.session_state.similarity.calculate_similarity()
    update_tracking(df_tracks)

    st.session_state.playlist_links.append(playlist_url)
    st.session_state.playlist_names.append(playlist_name)


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


def display_spotify_recommendations():
    """Method deals with displaying the Spotify recommendations in the form of Spotify iFrames for each recommendation.

    This section is composed of two columns, with 30 recommendations split evenly between them creating a 15 x 2 table.
    """
    st.markdown("#### Recommended Tracks")

    col1, col2 = st.columns(2)
    count = 0
    rec_df = st.session_state.similarity.get_top_n(30)
    for index, row in rec_df.iterrows():
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


def playlist_to_df(playlist: dict):
    """Method transforms playlist information in dictionary form to a playlist dataframe
    Args:
        playlist (dict): Playlist information in a dictionary, keys are features and values are a list.

    Returns:
        (DataFrame): A playlist dataframe.
    """
    target_df = pd.DataFrame.from_dict(playlist)
    return target_df


def similarity_visualization():
    """This method creates the similarity visualization of the dataset tracks to the created dataset feature vector.

    Returns:
        (Pyplot Figure): Figure for visualization by Streamlit
    """
    df = pd.DataFrame(st.session_state.similarity.access_similarity_scores(),
                           columns=['sim_score'])  # Access similarity scores of the process

    st.markdown("#### Playlist Similarity to Track Dataset")
    sns.set_style('whitegrid')
    fig, axes = plt.subplots(1, 1, figsize=(12, 4))

    g = sns.histplot(data=df,
                     x='sim_score',
                     kde=True,
                     color='red',
                     ax=axes)

    axes.set_yscale('log')
    axes.set_xscale('log')
    axes.set_xlabel('Similarity Values (Log)')
    axes.set_ylabel('Frequency')
    return fig


def create_feature_weighting(maximum=12):
    """Creates a streamlit dropdown menu, providing a selection of features that the user can select to weight.

    Args:
        maximum (int): The maximum number of features you can choose for weighting.

    Returns:
        (list): A list of selected feature names.
    """
    options = ['artist_pop', 'track_pop', 'danceability', 'energy', 'loudness', 'speechiness', 'acousticness',
               'instrumentalness', 'liveness', 'valences', 'tempos', 'durations_ms', 'tempos']
    selected_option = st.multiselect('Select features to weight', options, max_selections=maximum)
    return selected_option


def retrieve_feature_defs():
    """Method retrieves the feature definitions from the `data/feature_def.txt` file.

    Returns:
        (str): The contents of the `feature_def.txt` file.
    """
    root_path = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    file_path = os.path.join(root_path, 'data', 'feature_def.txt')
    with open(file_path, 'r') as file:
        contents = file.read()
        return contents


## UI Linear Process##
if 'playlist_links' not in st.session_state:  # Initialize playlist history states
    st.session_state.playlist_links = []
    st.session_state.playlist_names = []
    st.session_state.similarity = None

# Mias welcome
st.title("MIAS")
st.markdown(
    "MIAS is the **M**usically **I**lliterate **A**id **S**ystem designed to help artists expand their "
    "performance playlist by finding similar songs that match features essential to them")


# User input
st.header("Search ")
playlist_url = st.text_input("Please insert playlist url here")
playlist_name = st.text_input("Please insert the playlist name here")

feature_def_section()

with st.expander('Feature weighting (Optional)', expanded=False):
    st.session_state.weighted_features = create_feature_weighting()

submit_button = st.button("Submit")
if submit_button:
    if playlist_url != "" and playlist_name != "":
        playlist_submission()


search_history_section()


search_results_section()
