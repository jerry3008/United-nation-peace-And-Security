import csv
from datetime import datetime
from urllib.request import urlopen
from io import StringIO
import streamlit as st
import altair as alt
import matplotlib.pyplot as plt 
from streamlit_folium import folium_static
import folium
import pandas as pd

# Title and Header
st.title('Peace and Conflict Data')
st.header('Using Python and Streamlit')
st.write('UN Peace and Conflict')

# Load data from URL
data_url = "https://api.psdata.un.org/public/data/DOS-INDICATORS/CSV"
peace_conflict = pd.read_csv(data_url)


# Display data types
print(peace_conflict.dtypes)


# Display the DataFrame in Streamlit
st.dataframe(peace_conflict)
