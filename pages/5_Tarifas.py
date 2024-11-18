import streamlit as st
import os
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
from PIL import Image
import base64
from datetime import datetime, timedelta

st.set_page_config(page_title="Tarifas", layout="wide")
st.html("<style>[data-testid='stHeaderActionElements'] {display: none;}</style>")
st.markdown("""
    <style>
        * {
            font-family: 'Overpass', sans-serif !important;
        }
    </style>
""", unsafe_allow_html=True)