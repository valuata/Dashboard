import streamlit as st
import pandas as pd
import plotly.graph_objs as go
from datetime import datetime, timedelta

st.set_page_config(page_title="Carga", layout="wide")
st.html("<style>[data-testid='stHeaderActionElements'] {display: none;}</style>")
st.markdown("""
    <style>
        * {
            font-family: 'Overpass', sans-serif !important;
        }
    </style>
""", unsafe_allow_html=True)

def aggregate_data(data, frequency):
    data = data.set_index(['id_subsistema', 'din_instante'])

    # Adjusting the frequency for resampling
    if frequency == 'Diário':
        data = data.groupby(level='id_subsistema').resample('D', level='din_instante').last()
    elif frequency == 'Semanal':
        # Resample to get the average of the last week, starting week on Saturday
        data = data.groupby(level='id_subsistema').resample('W-SAT', level='din_instante').last()
    elif frequency == 'Mensal':
        # Resample to get the average value for each month, last day of the month
        data = data.groupby(level='id_subsistema').resample('M', level='din_instante').last()

    data = data.reset_index()
    
    return data[['din_instante', 'id_subsistema', 'val_cargaenergiamwmed']]


st.title("Carga")
carga_data = pd.read_csv('Carga_Consumo_atualizado.csv')
carga_data['din_instante'] = pd.to_datetime(carga_data['din_instante'].str.slice(0, 10), format="%Y-%m-%d")

# Frequency and Metric Selection
frequency = st.selectbox("Frequência", ['Diário', 'Semanal', 'Mensal'], index=2)  # Start with 'Mensal'
metric = st.selectbox("Métrica", ['MWmed', '% Carga Máxima'])

# Date Range Control
min_date = carga_data['din_instante'].min().date()
max_date = carga_data['din_instante'].max().date()

# Calculate the date range for the last 5 years
five_years_ago = max_date - timedelta(days=5*365)

# Date Range Slider for general selection
start_date_slider, end_date_slider = st.slider(
    "Selecione o intervalo de datas",
    min_value=min_date,
    max_value=max_date,
    value=(five_years_ago, max_date),
    format="YYYY-MM-DD"
)

# Display date inputs side by side using st.columns()
col1, col2 = st.columns(2)
with col1:
    start_date_input = st.date_input("Início", min_value=min_date, max_value=max_date, value=start_date_slider)
with col2:
    end_date_input = st.date_input("Fim", min_value=min_date, max_value=max_date, value=end_date_slider)

# Use the precise date input values for filtering
start_date = start_date_input
end_date = end_date_input

# Apply filters on the data
filtered_data = carga_data[(carga_data['din_instante'] >= pd.to_datetime(start_date)) & 
                           (carga_data['din_instante'] <= pd.to_datetime(end_date))]

# Aggregate the data based on selected frequency
agg_data = aggregate_data(filtered_data, frequency)

if not agg_data.empty:
    # Prepare the stacked bar chart
    fig = go.Figure()
    # Define subsystems and their respective colors (ensure the sequence SE, S, NE, N is followed)
    subsystems = ['SE/CO', 'S', 'NE', 'N']
    colors = ['#323e47', '#68aeaa', '#6b8b89', '#a3d5ce']
    
    # Add a trace for each subsystem (ensure the sequence SE, S, NE, N)
    for i, subsystem in enumerate(subsystems):
        subsystem_data = agg_data[agg_data['id_subsistema'] == subsystem]
        if not subsystem_data.empty:
            # Prepare custom data to show on hover
            custom_data = []
            for idx, row in subsystem_data.iterrows():
                se_val = agg_data[(agg_data['id_subsistema'] == 'SE/CO') & (agg_data['din_instante'] == row['din_instante'])]['val_cargaenergiamwmed'].values
                s_val = agg_data[(agg_data['id_subsistema'] == 'S') & (agg_data['din_instante'] == row['din_instante'])]['val_cargaenergiamwmed'].values
                ne_val = agg_data[(agg_data['id_subsistema'] == 'NE') & (agg_data['din_instante'] == row['din_instante'])]['val_cargaenergiamwmed'].values
                n_val = agg_data[(agg_data['id_subsistema'] == 'N') & (agg_data['din_instante'] == row['din_instante'])]['val_cargaenergiamwmed'].values
                # Calculate the sum for that date
                sum_val = (se_val[0] if len(se_val) > 0 else 0) + \
                          (s_val[0] if len(s_val) > 0 else 0) + \
                          (ne_val[0] if len(ne_val) > 0 else 0) + \
                          (n_val[0] if len(n_val) > 0 else 0)
                custom_data.append([se_val[0] if len(se_val) > 0 else 0,
                                    s_val[0] if len(s_val) > 0 else 0,
                                    ne_val[0] if len(ne_val) > 0 else 0,
                                    n_val[0] if len(n_val) > 0 else 0,
                                    sum_val])
            # Add the bar trace for this subsystem with custom color
            fig.add_trace(go.Bar(
                x=subsystem_data['din_instante'],
                y=subsystem_data['val_cargaenergiamwmed'],  # The y-values based on the selected metric
                name=subsystem,
                marker_color=colors[i],  # Apply the color for the specific subsystem
                hovertemplate=( 
                    '%{x}: ' +  # Showing the date
                    'Soma: %{customdata[4]}<br>' +  # Total sum for the date
                    'SE: %{customdata[0]}<br>' +  # SE value
                    'S: %{customdata[1]}<br>' +  # S value
                    'NE: %{customdata[2]}<br>' +  # NE value
                    'N: %{customdata[3]}<br>' +  # N value
                    '<extra></extra>'  # Optional to remove extra information
                ),
                customdata=custom_data,
                legendgroup=subsystem  # Use the subsystem name for the legend group
            ))
    
    # Update the layout for the stacked bar chart
    fig.update_layout(
        title=f"Carga/Consumo - {frequency}",
        xaxis_title="Data",
        yaxis_title="Carga (MWmed)",
        barmode='stack',
        legend=dict(
            orientation="h",  # Horizontal legend
            yanchor="bottom", 
            y=-0.5,  # Position it below the graph, ensure it doesn't overlap the X axis labels
            xanchor="center",
            x=0.5
        ),
        width=1200
    )

    # Adjust x-axis settings based on frequency
    if frequency == 'Diário':
        fig.update_xaxes(dtick="D1", tickformat="%d-%m-%Y", title="Data (Diário)")  # For daily data
    elif frequency == 'Semanal':
        fig.update_xaxes(dtick="W1", tickformat="%d-%m-%Y", title="Data (Semanal)")  # For weekly data
        fig.update_xaxes(tickvals=agg_data['din_instante'], tickmode='array')
    else:  # Mensal
        fig.update_xaxes(dtick="M1", tickformat="%m-%Y", title="Data (Mensal)")  # For monthly data

    # Display the stacked bar chart
    st.plotly_chart(fig, use_container_width=True)
else:
    st.write("Sem informações disponíveis para a filtragem feita.")




# import streamlit as st
# import os
# import pandas as pd
# import plotly.express as px
# import plotly.graph_objs as go
# from PIL import Image
# import base64
# from datetime import datetime, timedelta

# st.set_page_config(page_title="Dashboard Valuata", layout="wide")


# # st.markdown("""
# #     <style>
# #         body {
# #             background-color: #ededef;
# #             font-family: 'Overpass Light', sans-serif;
# #             color: #656871;  /* Set default text color */
# #         }

# #         /* Customizing the sidebar and other elements */
# #         .sidebar .sidebar-content {
# #             background-color: #ededef;
# #         }

# #         .block-container {
# #             background-color: #ededef;
# #         }

# #         .st-bb {
# #             background-color: #ededef;
# #         }

# #         h1, h2, h3, h4, h5, h6, p, div {
# #             font-family: 'Overpass Light', sans-serif;
# #             color: #656871;  /* Set text color for headings and paragraphs */
# #         }

# #         /* Customize widget background colors and text color */
# #         .stSelectbox, .stSlider, .stDateInput, .stButton, .stTextInput {
# #             background-color: #ededef;
# #             color: #ededef;  /* Set text color for widgets */
# #         }

# #         /* Customize the button's background when hovered */
# #         .stButton button:hover {
# #             background-color: #ededef;
# #         }

# #         /* Customize the input widget text color */
# #         input, select, textarea {
# #             color: #ededef;
# #         }

# #         /* Change the color of the options in selectbox */
# #         .stSelectbox select {
# #             color: #ededef;
# #         }

# #     </style>
# #     <link href="https://fonts.googleapis.com/css2?family=Overpass:wght@300&display=swap" rel="stylesheet">
# # """, unsafe_allow_html=True)

# def aggregate_data(data, frequency):
#     data = data.set_index(['id_subsistema', 'din_instante'])

#     # Adjusting the frequency for resampling
#     if frequency == 'Diário':
#         data = data.groupby(level='id_subsistema').resample('D', level='din_instante').last()
#     elif frequency == 'Semanal':
#         # Resample to get the average of the last week, starting week on Saturday
#         data = data.groupby(level='id_subsistema').resample('W-SAT', level='din_instante').mean()
#     elif frequency == 'Mensal':
#         # Resample to get the average value for each month, last day of the month
#         data = data.groupby(level='id_subsistema').resample('M', level='din_instante').mean()

#     data = data.reset_index()
    
#     return data[['din_instante', 'id_subsistema', 'val_cargaenergiamwmed']]

# def aggregate_data_ena(data, frequency, metric_column):
#     if frequency == 'Diário':
#         # Use last daily record for each subsystem
#         data = data.groupby(['id_subsistema', data['ena_data'].dt.date]).agg({
#             metric_column: 'last'
#         }).reset_index()
#         data['ena_data'] = pd.to_datetime(data['ena_data'].astype(str))  # Ensure 'ena_data' is datetime

#     elif frequency == 'Semanal':
#         # Resample to weekly (end of week Friday)
#         data['week'] = data['ena_data'].dt.to_period('W').dt.end_time
#         data = data.groupby(['id_subsistema', 'week']).agg({
#             metric_column: 'last'
#         }).reset_index()
#         data['ena_data'] = data['week']  # Set 'ena_data' to end of each week
#         data.drop(columns=['week'], inplace=True)

#     elif frequency == 'Mensal':
#         # Resample to monthly
#         data['month'] = data['ena_data'].dt.to_period('M').dt.end_time
#         data = data.groupby(['id_subsistema', 'month']).agg({
#             metric_column: 'last'
#         }).reset_index()
#         data['ena_data'] = data['month']  # Set 'ena_data' to end of each month
#         data.drop(columns=['month'], inplace=True)

#     return data[['ena_data', 'id_subsistema', metric_column]] 


# #EARMMMM
# def aggregate_data_earm(data, frequency, metric):
#     data['ear_data'] = pd.to_datetime(data['ear_data'])  # Ensure ear_data is datetime
#     if frequency == 'Diário':
#         data = data.groupby(['id_subsistema', data['ear_data'].dt.date]).agg({metric: 'last'}).reset_index()
#         data['ear_data'] = pd.to_datetime(data['ear_data'].astype(str))
    
#     elif frequency == 'Semanal':
#         data['week'] = data['ear_data'].dt.to_period('W').dt.end_time
#         data = data.groupby(['id_subsistema', 'week']).agg({metric: 'last'}).reset_index()
#         data['ear_data'] = pd.to_datetime(data['week'])
#         data.drop(columns=['week'], inplace=True)

#     elif frequency == 'Mensal':
#         data['month'] = data['ear_data'].dt.to_period('M').dt.end_time
#         data = data.groupby(['id_subsistema', 'month']).agg({metric: 'last'}).reset_index()
#         data['ear_data'] = pd.to_datetime(data['month'])
#         data.drop(columns=['month'], inplace=True)

#     return data[['ear_data', 'id_subsistema', metric]]

# # Function to create the gauge charts, including a single SIM gauge
# def make_subsystem_gauge_charts(data, metric_column, sim_column):
#     fig = go.Figure()

#     # Order of gauges as per your request
#     gauges_order = ['SE', 'S', 'NE', 'N', 'SIM']

#     # Number of unique subsystems (SE, S, NE, N)
#     subsystems = ['SE', 'S', 'NE', 'N']
#     gauge_width = 1 / len(gauges_order)  # Total number of gauges

#     # Create the subsystem gauges in the required order (SE, S, NE, N)
#     for i, subsystem in enumerate(subsystems):
#         subsystem_data = data[data['id_subsistema'] == subsystem]
#         percentage = subsystem_data[metric_column].iloc[0]  # Get the percentage for the latest date

#         # Set the bar color based on the value
#         if percentage <= 50:
#             bar_color = "red"
#         elif percentage <= 75:
#             bar_color = "yellow"
#         else:
#             bar_color = "green"

#         # Create the gauge chart for each subsystem
#         fig.add_trace(go.Indicator(
#             mode="gauge+number",
#             value=percentage,
#             title={"text": f"{subsystem} - Atual"},
#             gauge={
#                 "axis": {"range": [None, 100]},  # 0 to 100%
#                 "bar": {"color": bar_color},  # Color of the bar based on the value
#                 "bgcolor": "black",  # Dark grey background color of the gauge
#                 "steps": [
#                     {"range": [0, 100], "color": "black"}  # Keep the background as dark grey
#                 ]
#             },
#             domain={'x': [i * gauge_width, (i + 1) * gauge_width], 'y': [0, 1]},  # Place the gauges side by side
#         ))

#     # Create the SIM gauge (always the last one)
#     sim_percentage = data[sim_column].max()  # Get the max value for the SIM gauge (you could also use .mean() or another aggregation)

#     # Set the bar color for SIM gauge
#     if sim_percentage <= 50:
#         sim_bar_color = "red"
#     elif sim_percentage <= 75:
#         sim_bar_color = "yellow"
#     else:
#         sim_bar_color = "green"

#     # Create the SIM gauge chart
#     fig.add_trace(go.Indicator(
#         mode="gauge+number",
#         value=sim_percentage,
#         title={"text": "SIM"},
#         gauge={
#             "axis": {"range": [None, 100]},  # 0 to 100%
#             "bar": {"color": sim_bar_color},  # Color of the bar based on the value
#             "bgcolor": "black",  # Dark grey background color of the gauge
#             "steps": [
#                 {"range": [0, 100], "color": "black"}  # Keep the background as dark grey
#             ]
#         },
#         domain={'x': [4 * gauge_width, 5 * gauge_width], 'y': [0, 1]},  # Position SIM gauge last
#     ))

#     # Update the layout to arrange the gauges in a row
#     fig.update_layout(
#         title="Capacidade atual utilizada (%):",
#         grid={'rows': 1, 'columns': 5},  # 5 gauges in one row: SE, S, NE, N, SIM
#         showlegend=False,
#         height=400
#     )

#     return fig

# #MAPAAA
# # Function to fetch unique years from filenames
# def get_year_options():
#     years = set()
#     for filename in os.listdir(IMAGE_DIR):
#         if filename.endswith('.png'):
#             year = filename.split('_')[0][:4]  # Extract YYYY from YYYYMM
#             years.add(year)
#     return sorted(years)

# # Function to fetch unique months from filenames
# def get_month_options():
#     months = set()
#     for filename in os.listdir(IMAGE_DIR):
#         if filename.endswith('.png'):
#             month = filename.split('_')[0][4:6]  # Extract MM from YYYYMM
#             months.add(month)
#     return sorted(months)

# # Function to fetch images based on the selected year, month, and type
# def fetch_images(year, month, tipo, forecast_year, forecast_month):
#     images = []
#     for filename in os.listdir(IMAGE_DIR):
#         if (year == "" or filename.startswith(year)) and \
#            (month == "" or filename[4:6] == month) and \
#            (tipo == "" or filename.split('_')[1] == tipo) and \
#            (forecast_year == "" or filename.endswith(f"_{forecast_year}{forecast_month}.png")):
#             images.append(filename)
#     return images

# # Function to extract dates from the filename
# def extract_dates_from_filename(filename):
#     # Extract the regular date (YYYYMM) and the prediction date (yyyymm)
#     parts = filename.split('_')
#     regular_date = parts[0]  # YYYYMM format
#     prediction_date = parts[-1].split('.')[0]  # yyyymm format

#     regular_year = regular_date[:4]
#     regular_month = regular_date[4:6]

#     pred_year = prediction_date[:4]
#     pred_month = prediction_date[4:6]

#     return regular_month, regular_year, pred_month, pred_year

# # Function to get the image name based on the TIPO
# def get_image_name(tipo, regular_month, regular_year, pred_month=None, pred_year=None, forecast_month=None, forecast_year=None):
#     if tipo == "SOLO":
#         # For SOLO type, no second date is included
#         name = "armazenamento de agua no solo (%)"
#         return f"{regular_year}/{regular_month} - {name}"

#     elif tipo == "ANOMALIA":
#         name = "anomalia - precipitação acumulada (mm)"
#     elif tipo == "PRECIPITACAO":
#         name = "previsão - precipitação acumulada (mm)"
#     else:
#         name = tipo  # In case there's a new type we don't know about

#     # If "Previsão", format like: YYYY/MM - name: description - yyyy/mm (forecast)
#     if forecast_month and forecast_year:
#         return f"{regular_year}/{regular_month} - {name} - {forecast_year}/{forecast_month}"
#     else:
#         # If forecast details are not provided, just show the regular and prediction dates
#         return f"{regular_year}/{regular_month} - {name} - {pred_year}/{pred_month}"


# # Function to fetch prediction years based on available filenames
# def get_prediction_year_options():
#     prediction_years = set()
#     for filename in os.listdir(IMAGE_DIR):
#         if filename.endswith('.png'):
#             parts = filename.split('_')
#             if len(parts) >= 3:
#                 prediction_year = parts[-1]  # Get the last part (YYYYMM)
#                 prediction_years.add(prediction_year)
#     return sorted(prediction_years)

# # # Function to fetch unique TIPO options from filenames
# # def get_tipo_options():
# #     tipos = set()
# #     for filename in os.listdir(IMAGE_DIR):
# #         if filename.endswith('.png'):
# #             parts = filename.split('_')
# #             if len(parts) >= 2:
# #                 tipo = parts[1]  # Get the second part (TIPO)
# #                 tipos.add(tipo)
# #     return sorted(tipos)

# # Function to fetch images based on the selected prediction year, TIPO, and AAAAMM
# def fetch_comparison_images(prediction_year, tipo=None, aaamm=None):
#     comparison_images = []
#     for filename in os.listdir(IMAGE_DIR):
#         if filename.endswith('.png'):
#             parts = filename.split('_')
#             if len(parts) >= 3:
#                 year_part = parts[-1]  # Get the last part (YYYYMM)
#                 tipo_part = parts[1]    # Get the second part (TIPO)
                
#                 # Check if the filename matches the filters
#                 if year_part == prediction_year:
#                     if tipo is None or tipo_part == tipo:
#                         if aaamm is None or filename.startswith(aaamm):
#                             comparison_images.append(filename)
#     return comparison_images


