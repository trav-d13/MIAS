import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt


st.title("MIAS")
st.markdown(
    "MIAS is the **M**usically **I**lliterate **A**id **S**ystem designed to help developing artists expand on the "
    "songs"
    "they perform, by providing recommendations based on their current performance choices. I have very little "
    "musical talent,"
    ", but stil want to help, hence the name. ")

uploaded_file = st.file_uploader('Upload your file here')

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.write(df.describe())
