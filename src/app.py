import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt


st.title("MIAS")
st.markdown(
    "MIAS is the **M**usically **I**lliterate **A**id **S**ystem designed to help developing artists expand their "
    "performance playlist")

playlist_url = st.text_input("Please insert playlist url here")

