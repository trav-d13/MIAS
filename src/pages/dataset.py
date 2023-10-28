import streamlit as st
import os
import pandas as pd


class Monitor:
    def __init__(self):
        self.file_name = 'dataset_growth.csv'
        self.root_path = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        self.file_path = os.path.join(self.root_path, 'data', self.file_name)
        self.history = pd.read_csv(self.file_path)
        self.history['date'] = pd.to_datetime(self.history['date'], format="%d-%m-%Y")
        self.history['time'] = pd.to_datetime(self.history['time'], format='%H:%M:%S')

    def determine_date_range(self):
        return self.history['date'].min(), self.history['date'].max()


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
                     max_value=max_date.to_pydatetime())

if start_date >= end_date:
    st.write("Please make sure that start date comes before end date")
