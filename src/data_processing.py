import os
import time
from datetime import datetime
import pandas as pd
import spotipy
import streamlit as st
from spotipy import SpotifyClientCredentials

"""This file forms the basis of Spotify data processing.

    Specifically, the extraction of Spotify track data from calls through the Spotify developer API.
    This file processes, transforms, and stores the collected data relating to tracks, acoustic analysis, and artists.
"""


def target_playlist_extraction(sp, url, name):
    """This method extracts all track information from a given target playlist
    Args:
        sp (Spotipy Authorization): The authorized spotipy credentials object
        url (str): The url of the playlist from which to extract information
        name (str): The name of the playlist

    Returns:
        (dict): A dictionary containing all features and information pertaining to the target playlist.
    """
    uri = url2uri(url)  # Extract the uri
    store = construct_storage()  # Create the info storage
    extract_tracks(sp, uri, store)  # Extract track information
    add_playlist_tracking(name, store)  # Add playlist information (name)
    save_data(store, 'target.csv')  # Save the data (Update tracks.csv) dataset
    return store


def url2uri(url):
    """Method extracts the uri from a given Spotify url

    Args:
        url (str): The Spotify playlist url
    Returns:
        (str): The uri of the Spotify playlist
    """
    return url.split('/')[-1].split('?')[0]


def top_playlist_extraction(sp):
    """Method extracts the tracks in the 20 top-performing playlists from a selection of countries
     The countries include: Australia, UK, USA, Canada, Jamaica, South Africa

     This method does not return any information, but stores it in the tracks.csv dataset file.

     Args:
         sp (Spotipy Authorization): The authorized spotipy credentials object
    """
    countries = ['AU', 'GB', 'US', 'CA', 'JM', 'ZA']

    tracks_store = construct_storage()  # Construct track info storage

    for country in countries:  # Iterate through countries
        print(f'Country: {country}')
        top_playlists, names = find_top_playlists(sp, country)  # Find top 20 playlists in each country

        for playlist, name in zip(top_playlists[:], names[:]):  # Iterate through playlists
            try:
                print(f'Playlist name: {name}')
                store = construct_storage()
                extract_tracks(sp, playlist, store)
                add_playlist_tracking(name, store)
                merge_stores(tracks_store, store)  # Merge the playlist information, by merging the data stored.
                time.sleep(2)  # Respect APi limits through a forced sleep
            except Exception:
                print(f"Error accessing playlist {name} tracks")
        print('-----------------------------------------------------------------------------')

    save_data(tracks_store)  # Save the data


def save_data(tracks_store, name='tracks.csv'):
    """Method deals with saving collected track data

    Note, this method removes all duplicate tracks, such that all tracks within the dataset are unique, always keeping
    most up-to-date representation of each track.

    Args:
        tracks_store (dict): The dictionary containing all information extracted about the tracks
        name (str): The name of the file to save the information to. Default is the tracks.csv dataset file.

    """
    root_path = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    file_path = os.path.join(root_path, 'data', name)
    df_new = pd.DataFrame.from_dict(tracks_store)  # Create a dataframe from the collected data
    df_old = pd.read_csv(file_path, index_col=0)  # Create dataframe from old values

    if df_old.shape[0] != 0 and name == "tracks.csv":  # Previously saved songs, requiring further processing to have unique values only
        df_combined = pd.concat([df_new, df_old], axis=0)
        df_unique = df_combined.drop_duplicates(subset='uris', keep='first')  # Drop duplicates (keeping most up to date)
        df_unique = df_unique.reset_index(drop=True)
        df_unique.to_csv(file_path, mode='w')
    else:
        df_new.to_csv(file_path, mode='w')


def construct_storage():
    """Method constructs the storage dictionary in which collected track information is stored during collection,
    and enables saving as a csv file.

    Returns:
        (dict): An dictionary with each of the features initialized as keys, with associated empty list values.
    """
    store_outline = {
        'uris': [],
        'names': [],
        'artist_names': [],
        'artist_uris': [],
        'artist_pop': [],
        'artist_genres': [],
        'albums': [],
        'track_pop': [],
        'danceability': [],
        'energy': [],
        'keys': [],
        'loudness': [],
        'modes': [],
        'speechiness': [],
        'acousticness': [],
        'instrumentalness': [],
        'liveness': [],
        'valences': [],
        'tempos': [],
        'types': [],
        'ids': [],
        'track_hrefs': [],
        'analysis_urls': [],
        'durations_ms': [],
        'time_signatures': [],
        'playlist_name': []
    }
    return store_outline


def retrieve_batch_info(playlist, store):
    """Method retrieves the essential information from the batch API call to enable simplified extraction

    Returns:
        (dict): A partially updated store of track information. This required further data extraction.
    """
    items = playlist['items']  # Extract items (A list containing information on the tracks)
    store = process_items(store, items)  # Extract info and store it.
    return store


def process_items(store, items):
    """This method extracts the information from the Spotipy `tracks()` API call.
    Information includes:
    - Track uri
    - Track name
    - Track album
    - Track popularity

    Args:
        store (dict): The object in which to store extracted information
        items (list): The list of track information generated from the Spotipy tracks API call

    Returns:
        (dict): An updated store of information

    """
    for item in items:
        track_uri = item['track']['uri'].split(':')[-1]  # Extract track uri only from the provided link
        store['uris'].append(track_uri)  # Retrieve track uri
        store['names'].append(item['track']['name'])  # Retrieve track name

        store['artist_uris'].append(item['track']['artists'][0]['uri'].split(':')[-1])  # Find artist uri

        store['artist_names'].append(item['track']['artists'][0]['name'])  # Access artist name

        store['albums'].append(item['track']['album']['name'])  # Access album names
        store['track_pop'].append(item['track']['popularity'])  # Access track popularity
    return store


def extract_artist_info(store, sp):
    """Method deals with extracting artist information from the `artists()` API call through Spotipy

    Args:
        store (dict): The object in which to store extracted information
        sp (Spotipy Authorization): The authorized spotipy credentials object
    """
    limit = 50
    offset = 0
    while offset < len(store['artist_uris']):
        if offset + limit > len(store['artist_uris']):  # If else, deals with batching
            artists_info = sp.artists(store['artist_uris'][offset: len(store['artist_uris'])])  # Gather artis info through API
        else:
            artists_info = sp.artists(store['artist_uris'][offset: offset + limit])  # Gather artis info through API

        for artist in artists_info['artists']:  # Extract popularity and genres from each artist
            store['artist_pop'].append(artist['popularity'])  # Access artist popularity
            store['artist_genres'].append(artist['genres'])  # Access artist genres

        offset = offset + limit


def extract_audio_features(store, sp):
    """Method deal with extracting audio analysis features for a given batch of tracks

    Args:
        store (dict): The object in which to store extracted information
        sp (Spotipy Authorization): The authorized spotipy credentials object
    """
    limit = 100
    offset = 0
    while offset < len(store['uris']):
        if offset + limit > len(store['uris']):   # If else, deals with batching of acoustic features
            track_info = sp.audio_features(store['uris'][offset: len(store['uris'])])
        else:
            track_info = sp.audio_features(store['uris'][offset: offset + limit])

        for track in track_info:  # For each track extract the necessary features and store it
            store['danceability'].append(track['danceability'])
            store['energy'].append(track['energy'])
            store['keys'].append(track['key'])
            store['loudness'].append(track['loudness'])
            store['modes'].append(track['mode'])
            store['speechiness'].append(track['speechiness'])
            store['acousticness'].append(track['acousticness'])
            store['instrumentalness'].append(track['instrumentalness'])
            store['liveness'].append(track['liveness'])
            store['valences'].append(track['valence'])
            store['tempos'].append(track['tempo'])
            store['types'].append(track['type'])
            store['ids'].append(track['id'])
            store['track_hrefs'].append(track['track_href'])
            store['analysis_urls'].append(track['analysis_url'])
            store['durations_ms'].append(track['duration_ms'])
            store['time_signatures'].append(track['time_signature'])

        offset = offset + limit


def merge_stores(tracks_store, store):
    """Method deals with merging one store into another
    Args:
        store (dict): The track storage object to be merged.
        tracks_store (dict): The larger object in which to merge store into
    """
    for key, value in store.items():
        tracks_store[key].extend(value)


def extract_tracks(sp, playlist_uri, store):
    """Method deals with extracting tracks from a given playlist
    Note, this method forms the cornerstone of extraction, providing track access from a playlist.

    Args:
        sp (Spotipy Authorization): The authorized spotipy credentials object
        playlist_uri (str): The URI of the Spotify playlist
        store (dict): The object in which to store extracted information
    """
    offset = 0
    limit = 100
    playlist = sp.playlist_tracks(playlist_uri, limit=2, offset=offset)  # Retrieve the initial batch of songs
    total_songs = playlist['total']  # Extract the total number of songs

    while offset < total_songs:
        time.sleep(2)
        playlist = sp.playlist_tracks(playlist_uri, limit=100, offset=offset)  # Retrieve batch of songs in playlist
        store = retrieve_batch_info(playlist, store)  # Retrieve batch information
        offset = offset + limit  # Update offset

    extract_artist_info(store, sp)  # Extract the artist features for each track
    extract_audio_features(store, sp)  # Extract the audio features for each track


def find_top_playlists(sp, country):
    """Method finds the top-20 playlists in a given country

    Args:
        sp (Spotipy Authorization): The authorized spotipy credentials object
        country (str): The ISO 3166-1 alpha-2 country code of where the playlist should be extracted from.

    Returns:
        uris (list): A list of uris linking to each of the found playlists
        names (list): A related list of playlist names corresponding to the uris
    """
    uris = []
    names = []
    playlists = sp.featured_playlists(country=country, limit=20)
    playlist_items = playlists['playlists']['items']

    for item in playlist_items:  # Extract the uri and name from each playlist
        uris.append(item['uri'].split(':')[-1])
        names.append(item['name'])
    return uris, names


def add_playlist_tracking(name, store):
    """Method assigns the playlist name to each of the tracks to allow for traceback

    Args:
        name (str): The name of the playlist
        store (dict): The object in which to store extracted information
    """
    store['playlist_name'] = [name] * len(store['uris'])


def update_tracking(df):
    """Method updates the `dataset_growth.csv` file when new tracks are added to the dataset to record dataset growth

    Args:
        df (DataFrame): The dataframe containing all stored tracks, including new additions
    """
    root_path = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))  # Read in the growth dataset
    file_path = os.path.join(root_path, 'data', 'dataset_growth.csv')
    tracking_df = pd.read_csv(file_path, index_col=0)

    current_time = datetime.now()  # Extract new features to update the growth dataset with
    new_length = df.shape[0]
    new_entry = pd.DataFrame.from_dict({'date': [current_time.strftime("%d-%m-%Y")],
                                        'time': [current_time.strftime("%H:%M:%S")],
                                        'track_count': [new_length]})

    tracking_df = pd.concat([tracking_df, new_entry], axis=0, ignore_index=True)  # Update growth dataset
    tracking_df.reset_index(drop=True)
    tracking_df.to_csv(file_path, mode='w')


if __name__ == "__main__":
    client_credentials_manager = SpotifyClientCredentials(client_id=st.secrets['CLIENT_ID'],
                                                          client_secret=st.secrets[
                                                              'CLIENT_SECRET'])  # Set up Spotify Credentials
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    top_playlist_extraction(sp)