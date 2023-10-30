import streamlit as st
import os
import pandas as pd
from matplotlib import pyplot as plt
import seaborn as sns
from sklearn.preprocessing import MinMaxScaler
import re


class Monitor:
    """Monitor class serves as a dataset monitor

    Attributes:
        history_name (str): Name of the history dataset file name
        tracks_name (str): Name of the tracks dataset file name
        root_path (Path): Path to the root of the project
        hist_path (Path): Path to the history dataset
        track_path (Path): Path to the tracks dataset
        history (DataFrame): History dataset as a dataframe
        tracks (DataFrame): Track dataset as a dataframe
    """
    def __init__(self):
        """Method constructs the dataset monitor for data analysis within this page"""
        self.history_name = 'dataset_growth.csv'
        self.tracks_name = 'tracks.csv'
        self.root_path = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        self.hist_path = os.path.join(self.root_path, 'data', self.history_name)
        self.track_path = os.path.join(self.root_path, 'data', self.tracks_name)

        self.history = pd.read_csv(self.hist_path)
        self.tracks = pd.read_csv(self.track_path)

        self.history['date'] = pd.to_datetime(self.history['date'], format="%d-%m-%Y")  # Format the date
        self.history['time'] = pd.to_datetime(self.history['time'], format='%H:%M:%S')  # Format the time

    def determine_date_range(self):
        """Method determines the date range in the dataset history file.

        Returns:
            start (datetime): The earliest date available in the dataset history file.
            end (datetime): The latest date available in the dataset history file.
        """
        return self.history['date'].min(), self.history['date'].max()

    def access_acoustic_sample_features(self):
        """Method samples the tracks dataset and selects acoustic features for visualization in the pairplot.

        Note, sampling is used here as the size of the tracks dataset would take a long time to render in a pairplot.

        Returns:
            (DataFrame): Sampled tracks dataframe containing select acoustic features.
        """
        track_sample = self.tracks.sample(frac=0.1, random_state=1)
        acoustics_df = track_sample[['danceability', 'energy', 'loudness', 'speechiness',
                                    'acousticness', 'instrumentalness']]
        return acoustics_df

    def access_specific_features(self, selection: list, sample=True):
        """Method allows for access to specific acoustic features in the tracks dataset

        Args:
            selection (list): A list of acoustic features
            sample (bool): If True, the features must be sampled. If False, the feature is not sampled.

        Returns:
            (DataFrame): A dataframe containing the specified feature.
        """
        if sample:
            track_sample = self.tracks.sample(frac=0.1, random_state=2)
        else:
            track_sample = self.tracks
        return track_sample[selection]

    def access_artist_names(self):
        """Method determines the unique artist names in the tracks dataset.

        Returns:
            (list): A list of unique artists available in the tracks dataset.
        """
        names = self.tracks['artist_names'].unique().tolist()
        return names

    def access_feature_definitions(self):
        """Method allows for the `data/feature_def` file to be read-in providing feature definitions

        Returns:
            (str): Feature definitions
        """
        def_file = os.path.join(self.root_path, 'data', 'feature_def.txt')
        with open(def_file, 'r') as file:
            contents = file.read()
            return contents


def datasets_download_section():
    """Method prepares the `tracks.csv` and the `dataset_growth.csv` files for download."""
    # Tracks download
    with open(st.session_state.monitor.track_path, 'rb') as file:
        data = file.read()

    st.download_button(
        label='Click to download tracks dataset',
        data=data,
        file_name='tracks.csv',
        key='download_dataset'
    )

    # Growth download
    with open(st.session_state.monitor.hist_path, 'rb') as history_file:
        data_hist = history_file.read()

    st.download_button(
        label='Click to download tracks growth dataset',
        data=data_hist,
        file_name='dataset_growth.csv',
        key='download_dataset_growth'
    )


def create_feature_selection(maximum=12):
    """Method creates a streamlit multiselection capability, in which a user can select acoustic featurs to be visualized

    Args:
        maximum (int): The maximum number of features that can be selected.

    Returns:
        (list): A list of selected feature names
    """
    options = ['artist_pop', 'track_pop', 'danceability', 'energy', 'loudness', 'speechiness', 'acousticness',
               'instrumentalness', 'liveness', 'valences', 'durations_ms', 'tempos']
    selected_option = st.multiselect('Select features', options, default='loudness', max_selections=maximum)
    return selected_option


def artist_matching(artists: str):
    """Method performs a regex search against all artists in the database, using the artists search query.

    Args:
        artists (str): A search pattern of artists names (expect the string to be of format name,name,name with no whitespaces)
    Returns:
        (list): A list of matching artist names which the user can then select from.
    """
    options = []
    artist_names = re.split(r',|\|', artists)
    pattern = re.compile(fr"\b(?:{'|'.join(map(re.escape, artist_names))})\b", re.IGNORECASE)
    names = st.session_state.monitor.access_artist_names()
    for name in names:
        matches = re.findall(pattern, name)
        if matches:
            options.append(name)
    return options


@st.cache_resource
def generate_growth_plot(start, end):
    """This method generates a line plot showcasing the number of unique tracks in the dataset over time, showcasing its growth

    Args:
        start (datetime): The starting datetime to visualize the dataset growth
        end (datetime): The end datetime to visualize the dataset growth

    Returns:
        (PyPlot Figure): A line plot figure showcasing the dataset growth over time
    """
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
    """This function generates a pair plot showcasing the relationship between acoustic analysis features of the tracks in the dataset.

    Returns:
        (PyPlot Figure): A pyplot figure showcasing the acoustic feature relationships
    """
    df = st.session_state.monitor.access_acoustic_sample_features()

    sns.set()
    g = sns.pairplot(df, diag_kind='kde')
    return g.fig


def generate_distribution(selection: list):
    """Method generates feature distibutions to allow feature comparisons.

    Note, all features are normalized within the same range [-1, 1] for comparative visualization purposes.

    Args:
        selection (list): A list of features, such that their distributions will be visually compared.

    Returns:
        (PyPlot Figure): A figure showcasing the various acoustic feature distributions
    """
    df = st.session_state.monitor.access_specific_features(selection)

    scaler = MinMaxScaler(feature_range=(-1, 1))  # Normalize the data between [-1, 1] for visual purposes
    columns = selection
    df[columns] = scaler.fit_transform(df[columns])

    sns.set()
    fig, ax = plt.subplots(figsize=(10, 6))

    for feature in selection:  # Overlay the feature distributions
        h = sns.kdeplot(data=df, x=feature, label=feature, fill=True)
    ax.set_title('Acoustic Feature Distribution')
    ax.set_xlabel('Value')
    ax.set_ylabel('Density')
    ax.legend()

    return fig


def generate_artist_comparison(selection: list, artist_filter: list):
    """Method generates a swarmplot enabling artist comparison across various acoustic features.
    Args:
        selection (list): A list of features, such that their distributions will be visually compared.
        artist_filter (list): A filter of artist names, if the distributions

    Returns:
        (PyPlot Figure): A swarmplot showing comparable artist acoustic features
    """
    selection.append('artist_names')
    df = st.session_state.monitor.access_specific_features(selection, sample=False)
    df = df[df['artist_names'].isin(artist_filter)]  # Filter df to keep arist only tracks
    selection.remove('artist_names')

    scaler = MinMaxScaler(feature_range=(-1, 1))  # Normalize the data between [-1, 1] for visual purposes
    columns = selection
    df[columns] = scaler.fit_transform(df[columns])

    sns.set()
    fig, ax = plt.subplots(figsize=(10, 6))
    h = sns.swarmplot(data=df, x=selection[0], y='artist_names', hue='artist_names', palette="Set2", legend=False)
    return fig


def date_sliders(start, end):
    """Method creates the dataset growth date sliders, in order to determine the start and end date for visualizatin

    Args:
        start (datetime): Earliest available date in the history dataset
        end (dadtetime): Latest available date in the history dataset.

    Returns:
        start_date (datetime): The slider selected start date
        end_date (datetime): The slider selected end date
    """
    start_date = st.slider(label='Select start date',
                           min_value=start.to_pydatetime(),
                           max_value=end.to_pydatetime())
    end_date = st.slider(label='Select end date',
                         min_value=start.to_pydatetime(),
                         max_value=end.to_pydatetime(),
                         value=max_date.to_pydatetime())
    return start_date, end_date


# Initialize session state
if 'monitor' not in st.session_state:
    st.session_state.monitor = Monitor()

# Dataset page intro
st.title("Spotify Dataset")
st.markdown("The below information details the collected Spotify track dataset.")
st.markdown("This dataset is updated bi-weekly with the latest playlists and is freely available to download.")

# Dataset growth section
st.header('Dataset Growth')
min_date, max_date = st.session_state.monitor.determine_date_range()
start_date, end_date = date_sliders(min_date, max_date)

if start_date >= end_date:
    st.write("Please make sure that start date comes before end date")
else:
    fig_1 = generate_growth_plot(start_date, end_date)
    st.pyplot(fig_1)

# Dataset information section
st.header('Dataset Information')
st.markdown('Please review the definitions tab in order to understand the available features.')
with st.expander('Feature Definitions', expanded=False):
    feature_defs = st.session_state.monitor.access_feature_definitions()
    for definition in feature_defs.split('\\n'):
        st.markdown(definition)

# Acoustic features (pairplot)
st.markdown('#### Acoustic Features')
st.markdown('Please note that the below graphic is rendered using a sample of the dataset and a select set of '
            'features to promote readability')
fig_2 = generate_pair_plot()
st.pyplot(fig_2)

# Track acoustic feature comparison
st.markdown('#### Track Features Distribution')
st.markdown('Please select a set of features to view their distributions in the dataset')
selected_features = create_feature_selection()

if len(selected_features) == 0:
    st.write('Please select a minimum of a single feature to be displayed')
else:
    fig_3 = generate_distribution(selected_features)
    st.pyplot(fig_3)

# Artist comparison
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
        fig_4 = generate_artist_comparison(selection=feature, artist_filter=artists)
        st.pyplot(fig_4)

# Dataset download
st.header('Datasets Download')
st.markdown('Please click the below button to download the Spotify tracks dataset as a csv file.')
if st.button('Prepare Dataset for Download'):
    datasets_download_section()

