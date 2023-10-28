import streamlit as st
import os
import pandas as pd
from matplotlib import pyplot as plt
import seaborn as sns
from sklearn.preprocessing import MinMaxScaler
import re


class Monitor:
    def __init__(self):
        self.history_name = 'dataset_growth.csv'
        self.tracks_name = 'tracks.csv'
        self.root_path = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        self.hist_path = os.path.join(self.root_path, 'data', self.history_name)
        self.track_path = os.path.join(self.root_path, 'data', self.tracks_name)

        self.history = pd.read_csv(self.hist_path)
        self.tracks = pd.read_csv(self.track_path)

        self.history['date'] = pd.to_datetime(self.history['date'], format="%d-%m-%Y")
        self.history['time'] = pd.to_datetime(self.history['time'], format='%H:%M:%S')

    def determine_date_range(self):
        return self.history['date'].min(), self.history['date'].max()

    def access_acoustic_sample_features(self):
        track_sample = self.tracks.sample(frac=0.1, random_state=1)
        acoustics_df = track_sample[['danceability', 'energy', 'loudness', 'speechiness',
                                    'acousticness', 'instrumentalness']]
        return acoustics_df

    def access_specific_features(self, selection: list, sample=True):
        if sample:
            track_sample = self.tracks.sample(frac=0.1, random_state=2)
        else:
            track_sample = self.tracks
        return track_sample[selection]

    def access_artist_names(self):
        names = self.tracks['artist_names'].unique().tolist()
        return names


def create_feature_selection(maximum=12):
    options = ['artist_pop', 'track_pop', 'danceability', 'energy', 'loudness', 'speechiness', 'acousticness',
               'instrumentalness', 'liveness', 'valences', 'durations_ms', 'tempos']
    selected_option = st.multiselect('Select features', options, default='loudness', max_selections=maximum)
    return selected_option


def artist_matching(artists: str):
    options = []
    artist_names = re.split(r',|\|', artists)
    pattern = re.compile(fr"\b(?:{'|'.join(map(re.escape, artist_names))})\b", re.IGNORECASE)
    names = st.session_state.monitor.access_artist_names()
    for name in names:
        matches = re.findall(pattern, name)
        if matches:
            options.append(name)
    print(options)
    return options


@st.cache_resource
def generate_growth_plot(start, end):
    df = st.session_state.monitor.history
    history_filtered = df[(df['date'] >= start) & (df['date'] <= end)]

    sns.set()
    fig, axes = plt.subplots(1, 1, figsize=(12, 6))
    h = sns.lineplot(data=history_filtered, x='date', y='track_count', color='black')
    axes.fill_between(history_filtered['date'], history_filtered['track_count'], alpha=0.2, color='red')

    axes.set_xlabel('Date')
    axes.set_ylabel('Track Count')

    return fig


@st.cache_resource
def generate_pair_plot():
    df = st.session_state.monitor.access_acoustic_sample_features()

    sns.set()
    g = sns.pairplot(df, diag_kind='kde')
    return g.fig


def generate_distribution(selection: list, artist_filter=None):
    if artist_filter is None:
        df = st.session_state.monitor.access_specific_features(selection)
    else:
        selection.append('artist_names')
        print(selection)
        df = st.session_state.monitor.access_specific_features(selection, sample=False)
        df = df[df['artist_names'].isin(artist_filter)]  # Filter df to keep arist only tracks
        selection.remove('artist_names')

    scaler = MinMaxScaler(feature_range=(-1, 1))  # Normalize the data
    columns = selection
    df[columns] = scaler.fit_transform(df[columns])

    sns.set()
    fig, ax = plt.subplots(figsize=(10, 6))

    if artist_filter is None:
        for feature in selection:
            h = sns.kdeplot(data=df, x=feature, label=feature, fill=True)
        ax.set_title('Acoustic Feature Distribution')
        ax.set_xlabel('Value')
        ax.set_ylabel('Density')
        ax.legend()
    else:
        h = sns.swarmplot(data=df, x=selection[0], y='artist_names', palette="Set2")

    return fig


if 'monitor' not in st.session_state:
    st.session_state.monitor = Monitor()

st.title("Spotify Dataset")
st.markdown("The below information details the collected Spotify track dataset.")
st.markdown("This dataset is updated bi-weekly with the latest playlists and is freely available to download.")

st.header('Dataset Growth')
min_date, max_date = st.session_state.monitor.determine_date_range()

start_date = st.slider(label='Select start date',
                       min_value=min_date.to_pydatetime(),
                       max_value=max_date.to_pydatetime())
end_date = st.slider(label='Select end date',
                     min_value=min_date.to_pydatetime(),
                     max_value=max_date.to_pydatetime(),
                     value=max_date.to_pydatetime())

if start_date >= end_date:
    st.write("Please make sure that start date comes before end date")
else:
    fig_1 = generate_growth_plot(start_date, end_date)
    st.pyplot(fig_1)


st.header('Dataset Information')

st.markdown('#### Acoustic Features')
st.markdown('Please note that the below graphic is rendered using a sample of the dataset and a select set of '
            'features to promote readability')

fig_2 = generate_pair_plot()
st.pyplot(fig_2)

st.markdown('#### Track Features Distribution')
st.markdown('Please select a set of features to view their distributions in the dataset')
selected_features = create_feature_selection()

if len(selected_features) == 0:
    st.write('Please select a minimum of a single feature to be displayed')
else:
    fig_3 = generate_distribution(selected_features)
    st.pyplot(fig_3)


st.markdown('#### Artist Comparison')
st.markdown('Please enter the name of the artist/ band and select from the available options below in the dataset')
st.markdown('Each name must be seperated by a comma and include no whitespaces')
st.markdown('This section aims to enable artist comparison and the underlying framework of how the recommendation bases its answers')

search = st.text_input('Please type name')
artist = []
if len(search) != 0:
    options = artist_matching(search)
    artists = st.multiselect(label='Please select from the available artist in the dataset', options=options)
    if len(artists) != 0:
        feature = create_feature_selection(maximum=1)
        fig_4 = generate_distribution(selection=feature, artist_filter=artists)
        st.pyplot(fig_4)



