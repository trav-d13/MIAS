import streamlit as st
import os
import pandas as pd


class Monitor:
    def __init__(self):
        self.file_name = 'dataset_growth.csv'
        root_path = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        self.file_path = os.path.join(root_path, 'data', self.file_name)
        self.history = pd.read_csv(self.file_path)


if 'monitor' not in st.session_state:
    st.session_state.monitor = Monitor()


st.title("Spotify Dataset")
st.markdown("The below information details the collected Spotify track dataset.")
st.markdown("This dataset is updated bi-weekly with the latest playlists and is freely available to download.")



