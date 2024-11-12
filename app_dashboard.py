import streamlit as st
import os
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
from PIL import Image
import base64
from datetime import datetime, timedelta

st.set_page_config(page_title="Dashboard Valuata", layout="wide")


# st.markdown("""
#     <style>
#         body {
#             background-color: #ededef;
#             font-family: 'Overpass Light', sans-serif;
#             color: #656871;  /* Set default text color */
#         }

#         /* Customizing the sidebar and other elements */
#         .sidebar .sidebar-content {
#             background-color: #ededef;
#         }

#         .block-container {
#             background-color: #ededef;
#         }

#         .st-bb {
#             background-color: #ededef;
#         }

#         h1, h2, h3, h4, h5, h6, p, div {
#             font-family: 'Overpass Light', sans-serif;
#             color: #656871;  /* Set text color for headings and paragraphs */
#         }

#         /* Customize widget background colors and text color */
#         .stSelectbox, .stSlider, .stDateInput, .stButton, .stTextInput {
#             background-color: #ededef;
#             color: #ededef;  /* Set text color for widgets */
#         }

#         /* Customize the button's background when hovered */
#         .stButton button:hover {
#             background-color: #ededef;
#         }

#         /* Customize the input widget text color */
#         input, select, textarea {
#             color: #ededef;
#         }

#         /* Change the color of the options in selectbox */
#         .stSelectbox select {
#             color: #ededef;
#         }

#     </style>
#     <link href="https://fonts.googleapis.com/css2?family=Overpass:wght@300&display=swap" rel="stylesheet">
# """, unsafe_allow_html=True)

def aggregate_data(data, frequency):
    data = data.set_index(['id_subsistema', 'din_instante'])

    # Adjusting the frequency for resampling
    if frequency == 'Diário':
        data = data.groupby(level='id_subsistema').resample('D', level='din_instante').last()
    elif frequency == 'Semanal':
        # Resample to get the average of the last week, starting week on Saturday
        data = data.groupby(level='id_subsistema').resample('W-SAT', level='din_instante').mean()
    elif frequency == 'Mensal':
        # Resample to get the average value for each month, last day of the month
        data = data.groupby(level='id_subsistema').resample('M', level='din_instante').mean()

    data = data.reset_index()
    
    return data[['din_instante', 'id_subsistema', 'val_cargaenergiamwmed']]

def aggregate_data_ena(data, frequency, metric_column):
    if frequency == 'Diário':
        # Use last daily record for each subsystem
        data = data.groupby(['id_subsistema', data['ena_data'].dt.date]).agg({
            metric_column: 'last'
        }).reset_index()
        data['ena_data'] = pd.to_datetime(data['ena_data'].astype(str))  # Ensure 'ena_data' is datetime

    elif frequency == 'Semanal':
        # Resample to weekly (end of week Friday)
        data['week'] = data['ena_data'].dt.to_period('W').dt.end_time
        data = data.groupby(['id_subsistema', 'week']).agg({
            metric_column: 'last'
        }).reset_index()
        data['ena_data'] = data['week']  # Set 'ena_data' to end of each week
        data.drop(columns=['week'], inplace=True)

    elif frequency == 'Mensal':
        # Resample to monthly
        data['month'] = data['ena_data'].dt.to_period('M').dt.end_time
        data = data.groupby(['id_subsistema', 'month']).agg({
            metric_column: 'last'
        }).reset_index()
        data['ena_data'] = data['month']  # Set 'ena_data' to end of each month
        data.drop(columns=['month'], inplace=True)

    return data[['ena_data', 'id_subsistema', metric_column]] 


#EARMMMM
def aggregate_data_earm(data, frequency, metric):
    data['ear_data'] = pd.to_datetime(data['ear_data'])  # Ensure ear_data is datetime
    if frequency == 'Diário':
        data = data.groupby(['id_subsistema', data['ear_data'].dt.date]).agg({metric: 'last'}).reset_index()
        data['ear_data'] = pd.to_datetime(data['ear_data'].astype(str))
    
    elif frequency == 'Semanal':
        data['week'] = data['ear_data'].dt.to_period('W').dt.end_time
        data = data.groupby(['id_subsistema', 'week']).agg({metric: 'last'}).reset_index()
        data['ear_data'] = pd.to_datetime(data['week'])
        data.drop(columns=['week'], inplace=True)

    elif frequency == 'Mensal':
        data['month'] = data['ear_data'].dt.to_period('M').dt.end_time
        data = data.groupby(['id_subsistema', 'month']).agg({metric: 'last'}).reset_index()
        data['ear_data'] = pd.to_datetime(data['month'])
        data.drop(columns=['month'], inplace=True)

    return data[['ear_data', 'id_subsistema', metric]]

# Function to create the gauge charts, including a single SIM gauge
def make_subsystem_gauge_charts(data, metric_column, sim_column):
    fig = go.Figure()

    # Order of gauges as per your request
    gauges_order = ['SE', 'S', 'NE', 'N', 'SIM']

    # Number of unique subsystems (SE, S, NE, N)
    subsystems = ['SE', 'S', 'NE', 'N']
    gauge_width = 1 / len(gauges_order)  # Total number of gauges

    # Create the subsystem gauges in the required order (SE, S, NE, N)
    for i, subsystem in enumerate(subsystems):
        subsystem_data = data[data['id_subsistema'] == subsystem]
        percentage = subsystem_data[metric_column].iloc[0]  # Get the percentage for the latest date

        # Set the bar color based on the value
        if percentage <= 50:
            bar_color = "red"
        elif percentage <= 75:
            bar_color = "yellow"
        else:
            bar_color = "green"

        # Create the gauge chart for each subsystem
        fig.add_trace(go.Indicator(
            mode="gauge+number",
            value=percentage,
            title={"text": f"{subsystem} - Atual"},
            gauge={
                "axis": {"range": [None, 100]},  # 0 to 100%
                "bar": {"color": bar_color},  # Color of the bar based on the value
                "bgcolor": "black",  # Dark grey background color of the gauge
                "steps": [
                    {"range": [0, 100], "color": "black"}  # Keep the background as dark grey
                ]
            },
            domain={'x': [i * gauge_width, (i + 1) * gauge_width], 'y': [0, 1]},  # Place the gauges side by side
        ))

    # Create the SIM gauge (always the last one)
    sim_percentage = data[sim_column].max()  # Get the max value for the SIM gauge (you could also use .mean() or another aggregation)

    # Set the bar color for SIM gauge
    if sim_percentage <= 50:
        sim_bar_color = "red"
    elif sim_percentage <= 75:
        sim_bar_color = "yellow"
    else:
        sim_bar_color = "green"

    # Create the SIM gauge chart
    fig.add_trace(go.Indicator(
        mode="gauge+number",
        value=sim_percentage,
        title={"text": "SIM"},
        gauge={
            "axis": {"range": [None, 100]},  # 0 to 100%
            "bar": {"color": sim_bar_color},  # Color of the bar based on the value
            "bgcolor": "black",  # Dark grey background color of the gauge
            "steps": [
                {"range": [0, 100], "color": "black"}  # Keep the background as dark grey
            ]
        },
        domain={'x': [4 * gauge_width, 5 * gauge_width], 'y': [0, 1]},  # Position SIM gauge last
    ))

    # Update the layout to arrange the gauges in a row
    fig.update_layout(
        title="Capacidade atual utilizada (%):",
        grid={'rows': 1, 'columns': 5},  # 5 gauges in one row: SE, S, NE, N, SIM
        showlegend=False,
        height=400
    )

    return fig


#PLDDD
def aggregate_data_pld(data, frequency):
    if frequency == 'Daily':
        data = data.groupby(['Submercado', data['Data'].dt.date]).agg({'Valor': 'mean'}).reset_index()
        data['Data'] = pd.to_datetime(data['Data'])

    elif frequency == 'Weekly':
        data['week'] = data['Data'].dt.to_period('W').dt.end_time
        data = data.groupby(['Submercado', 'week']).agg({'Valor': 'mean'}).reset_index()
        data['Data'] = data['week']
        data.drop(columns=['week'], inplace=True)

    elif frequency == 'Monthly':
        data['month'] = data['Data'].dt.to_period('M').dt.end_time
        data = data.groupby(['Submercado', 'month']).agg({'Valor': 'mean'}).reset_index()
        data['Data'] = data['month']
        data.drop(columns=['month'], inplace=True)

    return data[['Data', 'Submercado', 'Valor']]

# Aggregation function for candlestick chart
def aggregate_candlestick_data(data, frequency):
    if frequency == 'Daily':
        agg = data.groupby([data['Data'].dt.date, 'Submercado']).agg(
            Open=('Valor', 'first'),
            High=('Valor', 'max'),
            Low=('Valor', 'min'),
            Close=('Valor', 'last')
        ).reset_index()
        agg['Data'] = pd.to_datetime(agg['Data'])

    elif frequency == 'Weekly':
        data['week'] = data['Data'].dt.to_period('W').dt.end_time
        agg = data.groupby(['week', 'Submercado']).agg(
            Open=('Valor', 'first'),
            High=('Valor', 'max'),
            Low=('Valor', 'min'),
            Close=('Valor', 'last')
        ).reset_index()
        agg['Data'] = agg['week']
        agg.drop(columns=['week'], inplace=True)

    elif frequency == 'Monthly':
        data['month'] = data['Data'].dt.to_period('M').dt.end_time
        agg = data.groupby(['month', 'Submercado']).agg(
            Open=('Valor', 'first'),
            High=('Valor', 'max'),
            Low=('Valor', 'min'),
            Close=('Valor', 'last')
        ).reset_index()
        agg['Data'] = agg['month']
        agg.drop(columns=['month'], inplace=True)

    return agg[['Data', 'Submercado', 'Open', 'High', 'Low', 'Close']]


#MAPAAA
# Function to fetch unique years from filenames
def get_year_options():
    years = set()
    for filename in os.listdir(IMAGE_DIR):
        if filename.endswith('.png'):
            year = filename.split('_')[0][:4]  # Extract YYYY from YYYYMM
            years.add(year)
    return sorted(years)

# Function to fetch unique months from filenames
def get_month_options():
    months = set()
    for filename in os.listdir(IMAGE_DIR):
        if filename.endswith('.png'):
            month = filename.split('_')[0][4:6]  # Extract MM from YYYYMM
            months.add(month)
    return sorted(months)

# Function to fetch images based on the selected year, month, and type
def fetch_images(year, month, tipo, forecast_year, forecast_month):
    images = []
    for filename in os.listdir(IMAGE_DIR):
        if (year == "" or filename.startswith(year)) and \
           (month == "" or filename[4:6] == month) and \
           (tipo == "" or filename.split('_')[1] == tipo) and \
           (forecast_year == "" or filename.endswith(f"_{forecast_year}{forecast_month}.png")):
            images.append(filename)
    return images

# Function to extract dates from the filename
def extract_dates_from_filename(filename):
    # Extract the regular date (YYYYMM) and the prediction date (yyyymm)
    parts = filename.split('_')
    regular_date = parts[0]  # YYYYMM format
    prediction_date = parts[-1].split('.')[0]  # yyyymm format

    regular_year = regular_date[:4]
    regular_month = regular_date[4:6]

    pred_year = prediction_date[:4]
    pred_month = prediction_date[4:6]

    return regular_month, regular_year, pred_month, pred_year

# Function to get the image name based on the TIPO
def get_image_name(tipo, regular_month, regular_year, pred_month=None, pred_year=None, forecast_month=None, forecast_year=None):
    if tipo == "SOLO":
        # For SOLO type, no second date is included
        name = "armazenamento de agua no solo (%)"
        return f"{regular_year}/{regular_month} - {name}"

    elif tipo == "ANOMALIA":
        name = "anomalia - precipitação acumulada (mm)"
    elif tipo == "PRECIPITACAO":
        name = "previsão - precipitação acumulada (mm)"
    else:
        name = tipo  # In case there's a new type we don't know about

    # If "Previsão", format like: YYYY/MM - name: description - yyyy/mm (forecast)
    if forecast_month and forecast_year:
        return f"{regular_year}/{regular_month} - {name} - {forecast_year}/{forecast_month}"
    else:
        # If forecast details are not provided, just show the regular and prediction dates
        return f"{regular_year}/{regular_month} - {name} - {pred_year}/{pred_month}"


# Function to fetch prediction years based on available filenames
def get_prediction_year_options():
    prediction_years = set()
    for filename in os.listdir(IMAGE_DIR):
        if filename.endswith('.png'):
            parts = filename.split('_')
            if len(parts) >= 3:
                prediction_year = parts[-1]  # Get the last part (YYYYMM)
                prediction_years.add(prediction_year)
    return sorted(prediction_years)

# # Function to fetch unique TIPO options from filenames
# def get_tipo_options():
#     tipos = set()
#     for filename in os.listdir(IMAGE_DIR):
#         if filename.endswith('.png'):
#             parts = filename.split('_')
#             if len(parts) >= 2:
#                 tipo = parts[1]  # Get the second part (TIPO)
#                 tipos.add(tipo)
#     return sorted(tipos)

# Function to fetch images based on the selected prediction year, TIPO, and AAAAMM
def fetch_comparison_images(prediction_year, tipo=None, aaamm=None):
    comparison_images = []
    for filename in os.listdir(IMAGE_DIR):
        if filename.endswith('.png'):
            parts = filename.split('_')
            if len(parts) >= 3:
                year_part = parts[-1]  # Get the last part (YYYYMM)
                tipo_part = parts[1]    # Get the second part (TIPO)
                
                # Check if the filename matches the filters
                if year_part == prediction_year:
                    if tipo is None or tipo_part == tipo:
                        if aaamm is None or filename.startswith(aaamm):
                            comparison_images.append(filename)
    return comparison_images


# Sidebar Navigation
st.sidebar.header("Menu")
page = st.sidebar.selectbox("Escolha a página", ["Carga/Consumo", "ENA", "EARM", "PLD", "Tarifas", "Curva Forward", "Mapas"])


# Page: Carga/Consumo
if page == "Carga/Consumo":
    st.title("Carga")
    carga_data = pd.read_csv('Carga_Consumo_atualizado.csv')
    carga_data['din_instante'] = pd.to_datetime(carga_data['din_instante'].str.slice(0, 10), format="%Y-%m-%d")
    
    # Frequency and Metric Selection
    frequency = st.selectbox("Frequência", ['Diário', 'Semanal', 'Mensal'])
    metric = st.selectbox("Métrica", ['MWmed', '% Carga Máxima'])

    # Date Range Control
    min_date = carga_data['din_instante'].min().date()
    max_date = carga_data['din_instante'].max().date()

    # Date Range Slider for general selection
    start_date_slider, end_date_slider = st.slider(
        "Selecione o intervalo de datas",
        min_value=min_date,
        max_value=max_date,
        value=(min_date, max_date),
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

        # Define subsystems and their respective colors
        subsystems = ['SE', 'S', 'NE', 'N']
        colors = ['#323e47', '#68aeaa', '#6b8b89', '#a3d5ce']

        # Add a trace for each subsystem
        for i, subsystem in enumerate(subsystems):
            subsystem_data = agg_data[agg_data['id_subsistema'] == subsystem]
            if not subsystem_data.empty:
                # Prepare custom data to show on hover
                custom_data = []
                for idx, row in subsystem_data.iterrows():
                    se_val = agg_data[(agg_data['id_subsistema'] == 'SE') & (agg_data['din_instante'] == row['din_instante'])]['val_cargaenergiamwmed'].values
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
                    customdata=custom_data
                ))

        # Update the layout for the stacked bar chart
        fig.update_layout(
            title=f"Carga/Consumo - {frequency}",
            xaxis_title="Data",
            yaxis_title="Carga (MWmed)",
            barmode='stack',
            xaxis=dict(tickformat="%Y-%m-%d"),
            width=1200
        )

        # Adjust x-axis settings based on frequency
        if frequency == 'Diário':
            fig.update_xaxes(dtick="D1", tickformat="%d/%b", title="Data (Diário)")
        elif frequency == 'Semanal':
            fig.update_xaxes(dtick="W1", tickformat="%d/%b/%y", title="Data (Semanal)")
            fig.update_xaxes(tickvals=agg_data['din_instante'], tickmode='array')
        else:  # Mensal
            fig.update_xaxes(dtick="M1", tickformat="%b/%y", title="Data (Mensal)")

        # Display the stacked bar chart
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.write("Sem informações disponíveis para a filtragem feita.")



elif page == "ENA":
    # Read data
    ena_data = pd.read_csv("Ena_atualizado.csv")
    monthly_data = pd.read_csv('Mlt_atualizado.csv')
    monthly_data['Ano'] = monthly_data['Ano'].apply(lambda x: str(x).strip())
    media_row = monthly_data[monthly_data['Ano'] == 'media'].iloc[0]  # Extract "media" row
    ena_data['ena_data'] = pd.to_datetime(ena_data['ena_data'])
    
    # Title for the page
    st.title("ENA - Energia Natural Afluente")

    # Side-by-side metric selection
    col1, col2 = st.columns(2)

    # Primary filter: ENA BRUTA or ENA ARMAZENÁVEL
    with col1:
        ena_type = st.selectbox("ENA", ['ENA Bruta', 'ENA Armazenável'])

    # Secondary filter: MWmed or % MLT
    with col2:
        unit_type = st.selectbox("Métrica", ['MWmed', '% MLT'])

    # Map selected options to the appropriate DataFrame column
    metric_column = f"ena_{'bruta' if ena_type == 'ENA Bruta' else 'armazenavel'}_regiao_{'mwmed' if unit_type == 'MWmed' else 'percentualmlt'}"

    # Frequency and Date Range Selection for Bar Chart
    frequency = st.selectbox("Frequência", ['Diário', 'Semanal', 'Mensal'])

    # Custom date range selector using st.slider
    min_date = ena_data['ena_data'].min().date()
    max_date = ena_data['ena_data'].max().date()

    # Create a slider for selecting the date range
    start_date, end_date = st.slider(
        "Selecione o período", 
        min_value=min_date, 
        max_value=max_date, 
        value=(min_date, max_date), 
        format="YYYY-MM-DD"
    )

    # Display selected start and end dates as smaller placeholders (smaller buttons)
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input(
            label="Início",
            value=start_date,
            min_value=min_date,
            max_value=end_date,
            key="start_date_input"
        )
    with col2:
        end_date = st.date_input(
            label="Fim",
            value=end_date,
            min_value=start_date,
            max_value=max_date,
            key="end_date_input"
        )

    # Filter the data based on the selected date range (for the Bar chart only)
    filtered_data = ena_data[(ena_data['ena_data'] >= pd.to_datetime(start_date)) & 
                             (ena_data['ena_data'] <= pd.to_datetime(end_date))]

    # Multiple selection for subsystems with custom order
    ordered_subsystems = ['SE', 'S', 'NE', 'N']  # Define the custom order for subsystems
    selected_subsystems = st.multiselect(
        "Submercados", 
        ordered_subsystems,
        default=ordered_subsystems  # Set default selection to all subsystems
    )

    # Filter the data for the selected subsystems
    filtered_subsystem_data = filtered_data[filtered_data['id_subsistema'].isin(selected_subsystems)]

    # Aggregate data based on the selected frequency
    agg_data = aggregate_data_ena(filtered_subsystem_data, frequency, metric_column)

    # Plotting the bar chart with max/min lines
    if not agg_data.empty:
        fig = go.Figure()

        # Define a blue-ish color palette for subsystems
        colors = ['#323e47', '#68aeaa', '#6b8b89', '#a3d5ce']

        for idx, subsystem in enumerate(selected_subsystems):  # Loop over the selected subsystems
            subsystem_data = agg_data[agg_data['id_subsistema'] == subsystem]
            fig.add_trace(go.Bar(
                x=subsystem_data['ena_data'],
                y=subsystem_data[metric_column],
                name=f"{subsystem} (Bar)",
                marker_color=colors[idx % len(colors)]  # Assign color from the palette
            ))

        fig.update_layout(
            title=f"ENA - {ena_type} ({unit_type}) ({frequency})",
            xaxis_title="Date",
            yaxis_title=f"{ena_type} ({unit_type})",
            barmode='group'
        )

        st.plotly_chart(fig)
    else:
        st.write("Sem informações para a filtragem feita.")
    
    st.write("---")

    # Subsystem Max-Min Range graph, now based on the time slicer and subsystem filter
    st.write("### Histórico dos submercados")
    
    # Add Subsystem Filter for Max-Min Range graph
    selected_subsystem_max_min = st.selectbox(
        "Submercado",
        selected_subsystems,
        index=0  # Default to the first selection
    )
    
    # Extract historical data (not affected by the date range)
    historical_data = ena_data[ena_data['id_subsistema'] == selected_subsystem_max_min].copy()
    
    # Extract the month and year from the 'ena_data' column
    historical_data['month'] = historical_data['ena_data'].dt.month
    historical_data['year'] = historical_data['ena_data'].dt.year
    
    # Define the metric column based on selected ENA type (adjust this as per your logic)
    ena_type = "ena_bruta_regiao_mwmed"  # Replace this with the actual column name you are interested in
    
    # Group by 'month' and aggregate by max, min, and average values for the chosen ENA column (e.g., 'ena_bruta')
    monthly_max_min_avg = historical_data.groupby('month').agg({
        ena_type: ['max', 'min', 'mean']  # Add 'mean' to calculate the average
    }).reset_index()
    
    # Flatten the column names after aggregation
    monthly_max_min_avg.columns = ['month', 'max_value', 'min_value', 'avg_value']
    
    # Convert month number to month abbreviation (e.g., jan, feb, mar...)
    monthly_max_min_avg['month_abbr'] = monthly_max_min_avg['month'].apply(
        lambda x: datetime(2020, x, 1).strftime('%b').lower()  # Use %b for month abbreviation (jan, feb, mar, etc.)
    )
    
    # Filter the data based on the selected date range for the X-axis (ensure we only show months within the range)
    selected_months = pd.to_datetime(filtered_data['ena_data']).dt.month.unique()
    monthly_max_min_avg = monthly_max_min_avg[monthly_max_min_avg['month'].isin(selected_months)]
    
    # Load the "media" row from the MLT_atualizado DataFrame for the selected subsystem
    media_row = monthly_data[(monthly_data['Subsistema'] == selected_subsystem_max_min) & (monthly_data['Ano'] == 'media')]
    
    # Extract month columns from the 'media' row (e.g., (jan)MWmed, (fev)MWmed, ...)
    if not media_row.empty:
        media_row = media_row.iloc[0]  # Get the first row (there should only be one "media" row)
        
        # Extract the month columns by identifying columns with the pattern (e.g., (jan)MWmed, (fev)MWmed, ...)
        media_values = {}
        
        for col in media_row.index:
            if '(' in col and ')MWmed' in col:  # It's a month column (e.g., (jan)MWmed)
                # Extract month abbreviation (jan, fev, mar, etc.)
                # We need to extract the part before the closing parentheses and after the opening parentheses
                month_abbr = col.split('(')[1].split(')')[0]  # Extract month abbreviation (jan, feb, mar, etc.)
                month_translation = {
                    'jan': 'jan', 'fev': 'feb', 'mar': 'mar', 'abr': 'apr', 'mai': 'may', 'jun': 'jun',
                    'jul': 'jul', 'ago': 'aug', 'set': 'sep', 'out': 'oct', 'nov': 'nov', 'dez': 'dec'
                }
                month_abbr_translated = month_translation.get(month_abbr.lower(), month_abbr)  # .lower() ensures case insensitivity
                # Save the media value for this month abbreviation
                media_values[month_abbr_translated] = media_row[col]
        # Debugging: Check extracted media values
    else:
        media_values = {}

    month_translation = {
        'Jan': 'jan', 'Feb': 'fev', 'Mar': 'mar', 'Apr': 'abr', 'May': 'mai', 'Jun': 'jun',
        'Jul': 'jul', 'Aug': 'ago', 'Sep': 'set', 'Oct': 'out', 'Nov': 'nov', 'Dec': 'dez'
    }
    
    # Add the "media" line (dashed) to the plot
    if not monthly_max_min_avg.empty:
        fig = go.Figure()
    
        # Add the area between max and min values for each month
        fig.add_trace(go.Scatter(
            x=monthly_max_min_avg['month_abbr'],
            y=monthly_max_min_avg['max_value'],
            mode='lines',
            line=dict(width=0),
            showlegend=False
        ))
    
        fig.add_trace(go.Scatter(
            x=monthly_max_min_avg['month_abbr'],
            y=monthly_max_min_avg['min_value'],
            mode='lines',
            fill='tonexty',  # Fill the area between max and min values
            fillcolor='#646971',  # Light gray color for the area
            line=dict(width=0),
            showlegend=False,
            name="Range"
        ))
    
        # Add the average line
        fig.add_trace(go.Scatter(
            x=monthly_max_min_avg['month_abbr'],
            y=monthly_max_min_avg['avg_value'],
            mode='lines',
            name="ENA média",  # Add a label for the average line
            line=dict(dash='solid', width=2, color='#323e47')  # Style the average line (dashed and blue)
        ))
    
        # Add the "media" line (dashed) from the MLT_atualizado DataFrame
        if media_values:
            # Map the media values to the corresponding month abbreviation in the chart
            media_line_values = [media_values.get(month_abbr, None) for month_abbr in monthly_max_min_avg['month_abbr']]
    
            fig.add_trace(go.Scatter(
                x=monthly_max_min_avg['month_abbr'],
                y=media_line_values,
                mode='lines',
                name="Média MLT",
                line=dict(dash='dash', width=2, color='#a3d5ce')  # Dashed red line for "media" values
            ))
    
        # Style and layout updates for axes
        fig.update_layout(
            title=f"Análise histórica ({selected_subsystem_max_min})",
            xaxis_title="Mês",
            yaxis_title="ENA Bruta",
            showlegend=True
        )
    
        # Ensure that each month is displayed on the X-axis
        fig.update_xaxes(
            tickformat="%b",  # Show only month names (jan, feb, mar, etc.)
            dtick="M1"  # Set tick spacing to 1 month
        )
    
        # Display full values on the Y-axis
        fig.update_yaxes(tickformat=".0f")  # Format to show full values without abbreviation
    
        # Display the plot
        st.plotly_chart(fig)
    else:
        st.write("No data available for the selected filters.")




# Page: EARM
elif page == "EARM":
    st.title("Reservatórios")

    earm_data = pd.read_csv('EARM_atualizado.csv')
    earm_data['ear_data'] = pd.to_datetime(earm_data['ear_data'])  # Garantir que 'ear_data' é datetime

    # Get the latest available data from the database (the last day available)
    latest_date = earm_data['ear_data'].max()
    latest_data = earm_data[earm_data['ear_data'] == latest_date]

    # Create the gauge chart for each subsystem (Atual gauges + SIM gauge)
    fig_atual_sim = make_subsystem_gauge_charts(latest_data, 'ear_verif_subsistema_percentual', 'verif_max_ratio')
    st.plotly_chart(fig_atual_sim)  # Display both the Atual and SIM gauges first
    
    st.write("---")

    # Filters for the rest of the page
    frequency = st.selectbox("Frequência", ['Diário', 'Semanal', 'Mensal'])
    metric = st.selectbox("Métrica", ['MWmês', '% Capacidade Máxima'])

    # Date Range for precise control
    min_date = earm_data['ear_data'].min().date()
    max_date = earm_data['ear_data'].max().date()

    # Date Range Slider for general selection
    start_date_slider, end_date_slider = st.slider(
        "Selecione o intervalo de datas",
        min_value=min_date,
        max_value=max_date,
        value=(min_date, max_date),
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

    # Filter data based on the selected date range
    filtered_data = earm_data[(earm_data['ear_data'] >= pd.to_datetime(start_date)) & 
                              (earm_data['ear_data'] <= pd.to_datetime(end_date))]

    # Define the column for the selected metric
    if metric == 'MWmês':
        metric_column = 'ear_verif_subsistema_mwmes'
    else:  # If it's % Capacidade Máxima
        metric_column = 'ear_verif_subsistema_percentual'

    # Aggregate the data based on the selected frequency
    agg_data = aggregate_data_earm(filtered_data, frequency, metric_column)

    # Calculate the 'ear_max_subsistema' line for each subsystem and aggregation
    if metric == 'MWmês':
        agg_data['ear_max_subsistema'] = agg_data.groupby('id_subsistema')[metric_column].transform('max')

    # Stacked Bar Chart for all subsystems (only when MWmês is selected)
    if metric == 'MWmês':  # Only show stacked bar chart for MWmês metric
        if not agg_data.empty:
            # Prepare data for stacked bar chart
            fig_stacked = go.Figure()

            # Set the correct order for subsystems: SE, S, NE, N
            subsystems = ['SE', 'S', 'NE', 'N']
            colors = ['#323e47', '#68aeaa', '#6b8b89', '#a3d5ce']  # The corresponding colors for each subsystem

            # Collect the data for each subsystem for each date
            for i, subsystem in enumerate(subsystems):
                subsystem_data = agg_data[agg_data['id_subsistema'] == subsystem]
                if not subsystem_data.empty:
                    # Prepare customdata: List of values for SE, S, NE, N and the sum
                    custom_data = []
                    for idx, row in subsystem_data.iterrows():
                        # Calculate the values for SE, S, NE, N for the same date
                        se_val = agg_data[(agg_data['id_subsistema'] == 'SE') & (agg_data['ear_data'] == row['ear_data'])][metric_column].values
                        s_val = agg_data[(agg_data['id_subsistema'] == 'S') & (agg_data['ear_data'] == row['ear_data'])][metric_column].values
                        ne_val = agg_data[(agg_data['id_subsistema'] == 'NE') & (agg_data['ear_data'] == row['ear_data'])][metric_column].values
                        n_val = agg_data[(agg_data['id_subsistema'] == 'N') & (agg_data['ear_data'] == row['ear_data'])][metric_column].values
                        
                        # Sum the values for the current date
                        sum_val = (se_val[0] if len(se_val) > 0 else 0) + \
                                  (s_val[0] if len(s_val) > 0 else 0) + \
                                  (ne_val[0] if len(ne_val) > 0 else 0) + \
                                  (n_val[0] if len(n_val) > 0 else 0)
                        
                        # Append the custom data for this date
                        custom_data.append([se_val[0] if len(se_val) > 0 else 0,
                                            s_val[0] if len(s_val) > 0 else 0,
                                            ne_val[0] if len(ne_val) > 0 else 0,
                                            n_val[0] if len(n_val) > 0 else 0,
                                            sum_val])

                    # Add trace for each subsystem in the correct order with specified colors
                    fig_stacked.add_trace(go.Bar(
                        x=subsystem_data['ear_data'], 
                        y=subsystem_data[metric_column],  # The y-values are based on the selected metric
                        name=subsystem,
                        marker_color=colors[i],  # Assign the specific color to the subsystem
                        hovertemplate=(
                            '%{x}: ' +  # Showing the date
                            'Soma: %{customdata[4]}<br>' +  # Total sum for the date
                            'SE: %{customdata[0]}<br>' +  # SE value
                            'S: %{customdata[1]}<br>' +  # S value
                            'NE: %{customdata[2]}<br>' +  # NE value
                            'N: %{customdata[3]}<br>' +  # N value
                            '<extra></extra>'  # Optional to remove extra information
                        ),
                        customdata=custom_data
                    ))

            # Update the layout for the stacked bar chart
            fig_stacked.update_layout(
                title=f"EARM - {metric} ({frequency})",
                xaxis_title="Data",
                yaxis_title=metric,
                barmode='stack',
                xaxis=dict(tickformat="%Y-%m-%d"),
            )

            # Display the stacked bar chart
            st.plotly_chart(fig_stacked)
            st.write("---")


    # Iterate through all subsystems (SE, S, NE, N) to plot individual bar charts
    if not agg_data.empty:
        subsystems = ['SE', 'S', 'NE', 'N']
        for subsystem in subsystems:
            subsystem_data = agg_data[agg_data['id_subsistema'] == subsystem]
            
            if not subsystem_data.empty:
                fig = go.Figure()

                # Add bars for the current subsystem
                fig.add_trace(go.Bar(
                    x=subsystem_data['ear_data'], 
                    y=subsystem_data[metric_column],  # 'y' should be metric_column here
                    name=subsystem, 
                    marker_color=colors[subsystems.index(subsystem)],  # Set the color based on the subsystem
                ))

                # Add a line for 'ear_max_subsistema' if the metric is 'MWmês'
                if metric == 'MWmês':
                    fig.add_trace(go.Scatter(
                        x=subsystem_data['ear_data'], 
                        y=subsystem_data['ear_max_subsistema'],
                        mode='lines', 
                        name=f"{subsystem} Max",
                        line=dict(dash='dash', width=2),
                    ))

                # Update the layout of the graph
                fig.update_layout(
                    title=f"EARM - {subsystem} - {metric} ({frequency})",
                    xaxis_title="Data",
                    yaxis_title=metric,
                    barmode='group',
                    xaxis=dict(tickformat="%Y-%m-%d"),
                )

                # Display the figure for the current subsystem
                st.plotly_chart(fig)

    else:
        st.write("Nenhum dado disponível para os filtros selecionados.")



    
    # Add "Atual" section with gauge charts
    # st.write("### Atual")

    # Create the gauge chart for each subsystem



# Page: PLD
elif page == "PLD":
    pld_data = pd.read_csv("PLD Horário Comercial Historico.csv")
    # Ensure date format is consistent
    pld_data['Data'] = pd.to_datetime(pld_data['Data'])
    
    # Title and Filters
    st.title("PLD")
    st.write("### Em construção")
    
    # Select chart type and frequency
    chart_type = st.selectbox("Select Chart Type", ['Area Chart', 'Candlestick Chart'])
    frequency = st.selectbox("Select Frequency", ['Daily', 'Weekly', 'Monthly'])
    
    # Date range filters
    st.write("### Date Range for Analysis")
    min_date = pld_data['Data'].min().date()
    max_date = pld_data['Data'].max().date()
    
    start_date = st.date_input("Start Date", min_date, min_value=min_date, max_value=max_date)
    end_date = st.date_input("End Date", max_date, min_value=min_date, max_value=max_date)
    
    # Apply Filters Button
    apply_filters = st.button("Apply Filters")
    # Show the chart only if Apply Filters is clicked
    if apply_filters:
        # Filter data based on date range
        filtered_data = pld_data[(pld_data['Data'] >= pd.to_datetime(start_date)) & 
                                 (pld_data['Data'] <= pd.to_datetime(end_date))]
    
        if chart_type == 'Area Chart':
            if not filtered_data.empty:
                fig = go.Figure()
                for subsystem in filtered_data['Submercado'].unique():
                    subsystem_data = filtered_data[filtered_data['Submercado'] == subsystem]
                    fig.add_trace(go.Scatter(
                        x=subsystem_data['Data'],
                        y=subsystem_data['Valor'],
                        mode='lines',
                        name=f"{subsystem} (Area)"
                    ))
    
                fig.update_layout(
                    title=f"PLD - {frequency} Area Chart",
                    xaxis_title="Date",
                    yaxis_title="PLD Value"
                )
    
                st.plotly_chart(fig)
            else:
                st.write("No data available for the selected filters.")
    
        elif chart_type == 'Candlestick Chart':
            # Aggregate data for candlestick chart
            agg_data = aggregate_candlestick_data(filtered_data, frequency)
    
            if not agg_data.empty:
                fig = go.Figure()
                for subsystem in agg_data['Submercado'].unique():
                    subsystem_data = agg_data[agg_data['Submercado'] == subsystem]
                    fig.add_trace(go.Candlestick(
                        x=subsystem_data['Data'],
                        open=subsystem_data['Open'],
                        high=subsystem_data['High'],
                        low=subsystem_data['Low'],
                        close=subsystem_data['Close'],
                        name=f"{subsystem} (Candlestick)"
                    ))
    
                fig.update_layout(
                    title=f"PLD - {frequency} Candlestick",
                    xaxis_title="Date",
                    yaxis_title="PLD Value"
                )
    
                st.plotly_chart(fig)
            else:
                st.write("No data available for the selected filters.")



# Page: Tarifas
elif page == "Tarifas":
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

# Page: Curva Forward
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

# Page: Mapas
elif page == "Mapas":
    IMAGE_DIR = "Imagens Meteorologia"  # Replace with the actual path
    st.title("Mapas")

    # First Part: User Input for Year and Month (Already Working)

    # Get available year and month options
    years = get_year_options()
    months = get_month_options()

    # User input for year and month
    col1, col2 = st.columns(2)
    with col1:
        selected_year = st.selectbox("Ano", options=[""] + years)
    with col2:
        selected_month = st.selectbox("Mês", options=[""] + months)

    # Fetch and display images based on year and month selection
    selected_images = fetch_images(selected_year, selected_month, "", "", "")

    if selected_images:
        cols = st.columns(3)  # Create 3 columns
        for i, img_file in enumerate(selected_images):
            img_path = os.path.join(IMAGE_DIR, img_file)
            img = Image.open(img_path)

            # Extract TIPO and other information from the filename
            filename_without_ext = os.path.splitext(img_file)[0]
            tipo = filename_without_ext.split('_')[1]  # Extract type
            # Extract regular and prediction dates using the new function
            regular_month, regular_year, pred_month, pred_year = extract_dates_from_filename(img_file)

            # Get the formatted image name
            formatted_name = get_image_name(tipo, regular_month, regular_year, pred_month, pred_year)

            # Resize image (optional)
            img.thumbnail((200, 200))

            with cols[i % 3]:  # Use modulo to place images in columns
                st.image(img, caption=formatted_name)
    else:
        st.write("Não há imagens para a combinação de datas selecionada.")

    # Second Part: Comparison Section (up to 4 filters)
    st.write("---")
    col3, col4, col5 = st.columns(3)
    with col3:
        st.header("Comparação")
    # Initialize the list of selected filters in session state
    if 'selected_filters' not in st.session_state:
        st.session_state.selected_filters = [{"year": "", "month": "", "tipo": "", "forecast_year": "", "forecast_month": ""}]

    # --- Filter Management: Independent of buttons ---
    # Button to add a filter
    with col4:
        add_button_clicked = st.button("➕")
        if add_button_clicked and len(st.session_state.selected_filters) < 4:
            st.session_state.selected_filters.append({"year": "", "month": "", "tipo": "", "forecast_year": "", "forecast_month": ""})
    with col5:
        # Button to remove the last filter
        remove_button_clicked = st.button("➖")
        if remove_button_clicked and len(st.session_state.selected_filters) > 1:
            st.session_state.selected_filters.pop()

    # Dynamically create filters for comparison (up to 4)
    filter_columns = st.columns(len(st.session_state.selected_filters))

    # Loop through the filters and create a set of filters for each image
    for i, filter_set in enumerate(st.session_state.selected_filters):
        with filter_columns[i]:
            st.subheader(f"Imagem {i + 1}")
            year = st.selectbox(f"Ano", options=[""] + years, key=f"year_{i}")
            month = st.selectbox(f"Mês", options=[""] + months, key=f"month_{i}")
            tipo = st.selectbox(f"Tipo", options=["", "SOLO", "ANOMALIA", "PRECIPITACAO"], key=f"tipo_{i}")

            # Separate Forecast Year and Month, ensure it's the lowercase format for previsao
            forecast_year = st.selectbox(f"Ano Previsão", options=[""] + years, key=f"forecast_year_{i}")
            forecast_month = st.selectbox(f"Mês Previsão ", options=[""] + months, key=f"forecast_month_{i}")

            # Update the filters in the session state
            st.session_state.selected_filters[i] = {
                "year": year, 
                "month": month, 
                "tipo": tipo, 
                "forecast_year": forecast_year, 
                "forecast_month": forecast_month
            }

    # Button to trigger image fetch and display
    if st.button("🔍 Gerar Comparação"):
        # Check if all filters are selected for each image
        for i, filter_set in enumerate(st.session_state.selected_filters):
            year = filter_set["year"]
            month = filter_set["month"]
            tipo = filter_set["tipo"]
            forecast_year = filter_set["forecast_year"]
            forecast_month = filter_set["forecast_month"]

            # If any filter is missing, skip this image
            if not all([year, month, tipo, forecast_year, forecast_month]):
                st.warning(f"Por favor, complete todos os filtros para a Imagem {i + 1}.")
                continue  # Skip this image if not all filters are selected

            selected_images = fetch_images(year, month, tipo, forecast_year, forecast_month)

            if selected_images:
                st.subheader(f"Imagem {i + 1}")
                cols = st.columns(3)  # Display in 3 columns
                for j, img_file in enumerate(selected_images):
                    img_path = os.path.join(IMAGE_DIR, img_file)
                    img = Image.open(img_path)

                    # Remove the file extension (.png) before splitting
                    filename_without_ext = os.path.splitext(img_file)[0]

                    # Extract TIPO from the filename (the second part of the filename, e.g., PRECIPITACAO)
                    tipo_from_filename = filename_without_ext.split('_')[1]  # Get the type from the second part of the filename

                    # Extract regular and prediction date (using new function)
                    regular_month, regular_year, pred_month, pred_year = extract_dates_from_filename(img_file)

                    # Get the formatted image name
                    formatted_name = get_image_name(tipo_from_filename, regular_month, regular_year, pred_month, pred_year, forecast_month, forecast_year)

                    # Resize image (optional)
                    img.thumbnail((200, 200))

                    with cols[j % 3]:  # Use modulo to place images in columns
                        st.image(img, caption=formatted_name)
            else:
                st.write(f"Sem resultados para a Imagem {i + 1} com os filtros selecionados.")

                