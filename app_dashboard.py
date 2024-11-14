import streamlit as st
import os
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
from PIL import Image
import base64
from datetime import datetime, timedelta

st.set_page_config(page_title="Dashboard Valuata", layout="wide")

# Sidebar Navigation
st.sidebar.header("Menu")
page = st.sidebar.selectbox("Escolha a página", ["Carga/Consumo", "ENA", "EARM", "PLD", "Tarifas", "Curva Forward", "Mapas"])

if page == "Tarifas":
    st.title("Tarifas")
    st.write("### Em construção")
    tarifas_data = pd.read_csv()
    if not tarifas_data.empty:
        subgroup = st.selectbox("Select Subgroup", tarifas_data['Subgrupo'].unique())
        modalidade = st.selectbox("Select Modalidade", tarifas_data['Modalidade'].unique())
        filtered_data = tarifas_data[(tarifas_data['Subgrupo'] == subgroup) & (tarifas_data['Modalidade'] == modalidade)]
        st.table(filtered_data[['Sigla', 'Resolução ANEEL', 'Início Vigência', 'Fim Vigência', 'TUSD', 'TE']])
    else:
        st.write("No data available.")

elif page == "Curva Forward":
    st.title("Curva Forward")
    st.write("### Em construção")
    curva_data = pd.read_csv()
    if not curva_data.empty:
        # Display data for selected subsystems and years
        fig = px.line(curva_data, x='DIA', y='SE/CO Convencional A+1', title="Curva Forward SE/CO Convencional A+1")
        st.plotly_chart(fig)
    else:
        st.write("No data available.")
