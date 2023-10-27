import os
import time

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

import pandas as pd

from credentials import set_credentials


def construct_storage():
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


def process_items(store, items):
    for item in items:
        track_uri = item['track']['uri'].split(':')[-1]
        store['uris'].append(track_uri)  # Retrieve track uri
        store['names'].append(item['track']['name'])  # Retrieve track name

        store['artist_uris'].append(item['track']['artists'][0]['uri'].split(':')[-1])  # Find artist uri

        store['artist_names'].append(item['track']['artists'][0]['name'])  # Access artist name

        store['albums'].append(item['track']['album']['name'])  # Access album names
        store['track_pop'].append(item['track']['popularity'])  # Access track popularity
    return store


def retrieve_batch_info(playlist, store):
    items = playlist['items']
    store = process_items(store, items)
    return store


def extract_artist_info(store, sp):
    limit = 50
    offset = 0
    while offset < len(store['artist_uris']):
        if offset + limit > len(store['artist_uris']):
            artists_info = sp.artists(store['artist_uris'][offset: len(store['artist_uris'])])
        else:
            artists_info = sp.artists(store['artist_uris'][offset: offset + limit])

        for artist in artists_info['artists']:
            store['artist_pop'].append(artist['popularity'])  # Access artist popularity
            store['artist_genres'].append(artist['genres'])  # Access artist genres

        offset = offset + limit


def extract_audio_features(store, sp):
    limit = 100
    offset = 0
    while offset < len(store['uris']):
        if offset + limit > len(store['uris']):
            track_info = sp.audio_features(store['uris'][offset: len(store['uris'])])
        else:
            track_info = sp.audio_features(store['uris'][offset: offset + limit])

        for track in track_info:
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
    for key, value in store.items():
        tracks_store[key].extend(value)


def extract_tracks(sp, playlist_uri, store):
    offset = 0
    limit = 100
    playlist = sp.playlist_tracks(playlist_uri, limit=2, offset=offset)  # Retrieve the initial batch of songs
    total_songs = playlist['total']  # Extract the total number of songs
    print(f"Total songs: {total_songs}")

    while offset < total_songs:
        time.sleep(2)
        playlist = sp.playlist_tracks(playlist_uri, limit=100, offset=offset)  # Retrieve batch of songs in playlist
        store = retrieve_batch_info(playlist, store)  # Retrieve batch information
        print(f"Current offset: {offset}")
        offset = offset + limit  # Update offset

    extract_artist_info(store, sp)
    extract_audio_features(store, sp)


def find_top_playlists(country):
    uris = []
    names = []
    playlists = sp.featured_playlists(country=country, limit=20)
    playlist_items = playlists['playlists']['items']
    for item in playlist_items:
        uris.append(item['uri'].split(':')[-1])
        names.append(item['name'])
    return uris, names


def add_playlist_tracking(name, store):
    store['playlist_name'] = [name] * len(store['uris'])


def record_playlists(top_playlists, names, playlist_store, name_store):
    playlist_store.extend(top_playlists)
    name_store.extend(names)


def save_data(tracks_store, name='tracks.csv'):
    root_path = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    file_path = os.path.join(root_path, 'data', name)
    df_new = pd.DataFrame.from_dict(tracks_store)  # Create a dataframe from the collected data
    df_old = pd.read_csv(file_path, index_col=0)  # Create dataframe from old values

    if df_old.shape[0] != 0 and name == "tracks.csv":  # Previously saved songs, requiring further processing to have unique values only
        df_combined = pd.concat([df_new, df_old], axis=0)
        df_unique = df_combined.drop_duplicates(subset='uris', keep='first')
        df_unique = df_unique.reset_index(drop=True)
        df_unique.to_csv(file_path, mode='w')
    else:
        df_new.to_csv(file_path, mode='w')


def top_playlist_extraction(sp):
    countries = ['AU', 'GB', 'US', 'CA', 'JM', 'ZA']

    playlist_store = []  # Store for playlist names
    name_store = []  # Construct playlist info storage
    tracks_store = construct_storage()  # Construct track info storage

    for country in countries[5:]:
        print(f'Country: {country}')
        top_playlists, names = find_top_playlists(country)

        for playlist, name in zip(top_playlists[:], names[:]):
            try:
                print(f'Playlist name: {name}')
                store = construct_storage()
                extract_tracks(sp, playlist, store)
                add_playlist_tracking(name, store)
                merge_stores(tracks_store, store)
                time.sleep(2)
            except Exception:
                print(f"Error accessing playlist {name} tracks")

        record_playlists(top_playlists, names, playlist_store, name_store)
        print('-----------------------------------------------------------------------------')

    save_data(tracks_store)


def target_playlist_extraction(sp, url, name):
    uri = url2uri(url)
    store = construct_storage()
    extract_tracks(sp, uri, store)
    add_playlist_tracking(name, store)
    save_data(store, 'target.csv')
    return store


def url2uri(url):
    return url.split('/')[-1].split('?')[0]


if __name__ == "__main__":
    set_credentials()

    client_credentials_manager = SpotifyClientCredentials(client_id=os.getenv('CLIENT_ID'),
                                                          client_secret=os.getenv('CLIENT_SECRET'))
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

    url = "https://open.spotify.com/playlist/799B2k7VQhsWeA2iQrun9f?si=345d3d94fb484f2c"

    # target_playlist_extraction(sp, url, "Rob Performance Playlist")
    top_playlist_extraction(sp)

